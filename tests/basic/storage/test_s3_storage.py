import io

import pytest
from botocore.exceptions import ClientError

from nerdd_link.storage import S3Storage


def _create_storage(mocker, **kwargs):
    client = mocker.Mock()
    mocker.patch("nerdd_link.storage.s3_storage.boto3.client", return_value=client)
    storage = S3Storage("http://s3.example.com", "my-bucket", "username", "password", **kwargs)
    return storage, client


def test_repr():
    storage = S3Storage(
        url="http://s3.example.com",
        bucket_name="my-bucket",
        username="my-secret-username",
        password="my-secret-password",
        max_spool_size=1024,
        multipart_part_size=5 * 1024 * 1024,
    )

    result = repr(storage)

    # make sure that username and password are not exposed
    assert "my-secret-username" not in result
    assert "my-secret-password" not in result
    assert "username='***'" in result
    assert "password='***'" in result
    assert "url='http://s3.example.com'" in result
    assert "bucket_name='my-bucket'" in result


def test_validation_lists_bucket(mocker):
    storage, client = _create_storage(mocker)

    storage.validate()

    client.list_objects_v2.assert_called_once_with(Bucket="my-bucket", MaxKeys=1)


def test_validation_propagates_client_error(mocker):
    storage, client = _create_storage(mocker)
    client.list_objects_v2.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied", "Message": "Access denied"}}, "ListObjectsV2"
    )

    with pytest.raises(ClientError):
        storage.validate()


def test_reads_object_into_seekable_handle(mocker):
    storage, client = _create_storage(mocker)
    body = io.BytesIO(b"content")
    client.get_object.return_value = {"Body": body}

    with storage.get_source_file_handle("source-1", "rb") as handle:
        assert handle.read() == b"content"
        assert handle.seek(0) == 0
        assert handle.read() == b"content"

    client.get_object.assert_called_once_with(Bucket="my-bucket", Key="sources/source-1")
    assert body.closed


def test_writes_small_object_on_close(mocker):
    storage, client = _create_storage(mocker)

    with storage.get_source_file_handle("source-1", "wb") as handle:
        handle.write(b"content")

    client.put_object.assert_called_once_with(
        Bucket="my-bucket", Key="sources/source-1", Body=b"content"
    )


def test_writes_multipart_object(mocker):
    part_size = 5 * 1024 * 1024
    first_part = b"a" * part_size
    storage, client = _create_storage(mocker, multipart_part_size=part_size)
    client.create_multipart_upload.return_value = {"UploadId": "upload-1"}
    client.upload_part.side_effect = [{"ETag": "part-1"}, {"ETag": "part-2"}]

    with storage.get_source_file_handle("source-1", "wb") as handle:
        handle.write(first_part)
        handle.write(b"tail")

    client.create_multipart_upload.assert_called_once_with(
        Bucket="my-bucket", Key="sources/source-1"
    )
    assert client.upload_part.call_args_list == [
        mocker.call(
            Bucket="my-bucket",
            Key="sources/source-1",
            UploadId="upload-1",
            PartNumber=1,
            Body=first_part,
        ),
        mocker.call(
            Bucket="my-bucket",
            Key="sources/source-1",
            UploadId="upload-1",
            PartNumber=2,
            Body=b"tail",
        ),
    ]
    client.complete_multipart_upload.assert_called_once_with(
        Bucket="my-bucket",
        Key="sources/source-1",
        UploadId="upload-1",
        MultipartUpload={
            "Parts": [
                {"ETag": "part-1", "PartNumber": 1},
                {"ETag": "part-2", "PartNumber": 2},
            ]
        },
    )


def test_aborts_multipart_upload_after_part_failure(mocker):
    part_size = 5 * 1024 * 1024
    storage, client = _create_storage(mocker, multipart_part_size=part_size)
    client.create_multipart_upload.return_value = {"UploadId": "upload-1"}
    client.upload_part.side_effect = RuntimeError("upload failed")
    handle = storage.get_source_file_handle("source-1", "wb")

    with pytest.raises(RuntimeError, match="upload failed"):
        handle.write(b"a" * part_size)

    with pytest.raises(OSError, match="multipart upload failed"):
        handle.raw.write(b"more")

    handle.close()

    client.abort_multipart_upload.assert_called_once_with(
        Bucket="my-bucket", Key="sources/source-1", UploadId="upload-1"
    )
    client.complete_multipart_upload.assert_not_called()
