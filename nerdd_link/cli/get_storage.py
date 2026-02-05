from typing import Optional

import rich_click as click

from ..storage import ChainedStorage, FileSystemStorage, MirroredStorage, Storage

__all__ = ["get_storage"]


def get_storage(
    data_dir: Optional[str],
    s3_url: Optional[str],
    s3_bucket: Optional[str],
    s3_username: Optional[str],
    s3_password: Optional[str],
    mirrored: bool = False,
) -> Storage:
    # TODO: after transition from file system to s3, allow only a single storage option
    if (
        s3_url is not None
        and s3_bucket is not None
        and s3_username is not None
        and s3_password is not None
    ):
        # TODO: replace
        # s3_storage = S3Storage(s3_url, s3_bucket, s3_username, s3_password)
        s3_storage = FileSystemStorage(data_dir)  # type: ignore[arg-type]
        if data_dir is not None:
            file_system_storage = FileSystemStorage(data_dir)
            if mirrored:
                return MirroredStorage(s3_storage, file_system_storage)
            else:
                return ChainedStorage(s3_storage, file_system_storage)
        else:
            return s3_storage
    elif data_dir is not None:
        return FileSystemStorage(data_dir)
    else:
        raise click.UsageError(
            "Either --data-dir or all S3 options (--s3-url, --s3-bucket, "
            "--s3-username, and --s3-password) must be provided."
        )
