import io
from shutil import copyfileobj
from tempfile import SpooledTemporaryFile
from typing import Any, BinaryIO, Dict, Iterator, List, Literal, Optional, cast

import boto3
from botocore.exceptions import ClientError

from .storage import Storage

__all__ = ["S3Storage"]


class _S3MultipartWriteRawIO(io.RawIOBase):
    """Stream writes to S3 without keeping the complete object in memory.

    S3 requires every multipart upload part except the last one to meet the minimum part size.
    The writer therefore buffers exactly one part, uploading it as soon as it is full. Closing
    the writer decides whether the buffered data is a small single-part object or the final part
    of a multipart upload.
    """

    def __init__(self, client: Any, bucket_name: str, key: str, multipart_part_size: int) -> None:
        super().__init__()
        self._client = client
        self._bucket_name = bucket_name
        self._key = key
        self._multipart_part_size = multipart_part_size
        self._buffer = bytearray()
        self._upload_id: Optional[str] = None
        self._parts: List[Dict[str, Any]] = []
        self._position = 0
        self._failed = False

    def writable(self) -> bool:
        return True

    def tell(self) -> int:
        return self._position

    def write(self, buffer: Any) -> int:
        if self.closed:
            raise ValueError("I/O operation on closed file.")
        if self._failed:
            raise OSError("Cannot write after the multipart upload failed.")

        # we don't know if this is the last write operation
        # -> we cannot upload the final part yet, even if it is smaller than the minimum part size
        # -> simply store to buffer and upload final part on close!

        data = memoryview(buffer).cast("B")
        size = len(data)
        offset = 0
        try:
            while offset < size:
                # Only full parts are uploaded here; S3 permits a smaller final part on close.
                chunk_size = min(
                    self._multipart_part_size - len(self._buffer),
                    size - offset,
                )
                self._buffer.extend(data[offset : offset + chunk_size])
                offset += chunk_size
                if len(self._buffer) == self._multipart_part_size:
                    self._upload_part()
        except Exception:
            self._fail()
            raise

        self._position += size
        return size

    def _upload_part(self) -> None:
        # create multipart upload if it has not been created yet
        if self._upload_id is None:
            response = self._client.create_multipart_upload(
                Bucket=self._bucket_name,
                Key=self._key,
            )
            self._upload_id = response["UploadId"]

        # upload the current buffer as a new part of the multipart upload
        part_number = len(self._parts) + 1
        response = self._client.upload_part(
            Bucket=self._bucket_name,
            Key=self._key,
            UploadId=self._upload_id,
            PartNumber=part_number,
            Body=bytes(self._buffer),
        )

        # S3 requires each part number and ETag when completing the multipart upload
        self._parts.append(
            {
                "ETag": response["ETag"],
                "PartNumber": part_number,
            }
        )
        self._buffer.clear()

    def _fail(self) -> None:
        self._failed = True
        if self._upload_id is not None:
            # abort multipart upload to avoid leaving an incomplete object in S3
            upload_id = self._upload_id
            self._upload_id = None
            try:
                self._client.abort_multipart_upload(
                    Bucket=self._bucket_name,
                    Key=self._key,
                    UploadId=upload_id,
                )
            except Exception:
                # ignore errors during abort (to avoid masking the original error)
                pass

    def close(self) -> None:
        if self.closed:
            return

        try:
            if not self._failed:
                # complete upload
                if self._upload_id is None:
                    # no full part was written
                    # -> we can use a single PUT request
                    self._client.put_object(
                        Bucket=self._bucket_name,
                        Key=self._key,
                        Body=bytes(self._buffer),
                    )
                else:
                    if self._buffer:
                        # final multipart upload part might be smaller than the minimum part size
                        # -> upload buffer now
                        self._upload_part()

                    self._client.complete_multipart_upload(
                        Bucket=self._bucket_name,
                        Key=self._key,
                        UploadId=self._upload_id,
                        MultipartUpload={"Parts": self._parts},
                    )
                    self._upload_id = None
        except Exception:
            self._fail()
            raise
        finally:
            self._buffer.clear()
            super().close()


class S3Storage(Storage):
    """Storage implementation that persists NERDD job data in an S3 bucket."""

    def __init__(
        self,
        url: str,
        bucket_name: str,
        access_key_id: str,
        secret_access_key: str,
        max_spool_size: int = 8 * 1024 * 1024,
        multipart_part_size: int = 8 * 1024 * 1024,
    ) -> None:
        if max_spool_size <= 0:
            raise ValueError("max_spool_size must be positive.")
        if multipart_part_size < 5 * 1024 * 1024:
            raise ValueError("multipart_part_size must be at least 5 MiB.")

        super().__init__("s3")
        self.url = url
        self.bucket_name = bucket_name
        self._max_spool_size = max_spool_size
        self._multipart_part_size = multipart_part_size
        self._client = boto3.client(
            "s3",
            endpoint_url=url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )

    def _validate(self) -> None:
        self._client.list_objects_v2(Bucket=self.bucket_name, MaxKeys=1)

    def _iter_directory(self, identifier: str) -> Iterator[str]:
        prefix = identifier.rstrip("/") + "/"
        continuation_token: Optional[str] = None
        while True:
            # collect query parameters
            kwargs: Dict[str, Any] = {
                "Bucket": self.bucket_name,
                "Prefix": prefix,
                "Delimiter": "/",
            }
            # add continuation token if we are not on the first page
            if continuation_token is not None:
                kwargs["ContinuationToken"] = continuation_token

            # get the next result page
            response = self._client.list_objects_v2(**kwargs)
            for object_info in response.get("Contents", []):
                key = object_info["Key"]
                if key != prefix:
                    yield key
            if not response.get("IsTruncated"):
                return
            continuation_token = response["NextContinuationToken"]

    def _get_binary_file_handle(self, identifier: str, mode: Literal["rb", "wb"]) -> BinaryIO:
        if mode == "rb":
            body = self._client.get_object(Bucket=self.bucket_name, Key=identifier)["Body"]
            spool = SpooledTemporaryFile(max_size=self._max_spool_size, mode="w+b")
            try:
                copyfileobj(body, spool)
                spool.seek(0)
            except Exception:
                spool.close()
                raise
            finally:
                body.close()
            return cast(BinaryIO, spool)
        else:  # mode == "wb"
            # return a writer that supports multipart uploads to S3 with bounded memory usage
            return io.BufferedWriter(
                _S3MultipartWriteRawIO(
                    self._client,
                    self.bucket_name,
                    identifier,
                    self._multipart_part_size,
                )
            )

    def _delete_file(self, identifier: str) -> None:
        self._client.delete_object(Bucket=self.bucket_name, Key=identifier)

    def _file_exists(self, identifier: str) -> bool:
        try:
            self._client.head_object(Bucket=self.bucket_name, Key=identifier)
            return True
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")
            if error_code in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise

    def __repr__(self) -> str:
        return (
            f"S3Storage("
            f"url={self.url!r}, "
            f"bucket_name={self.bucket_name!r}, "
            f"access_key_id='***', "
            f"secret_access_key='***', "
            f"max_spool_size={self._max_spool_size!r}, "
            f"multipart_part_size={self._multipart_part_size!r}"
            f")"
        )
