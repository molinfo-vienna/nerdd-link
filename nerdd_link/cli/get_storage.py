import logging
from typing import Optional

import rich_click as click

from ..storage import ChainedStorage, FileSystemStorage, MirroredStorage, S3Storage, Storage

__all__ = ["get_storage"]

logger = logging.getLogger(__name__)


def get_storage(
    data_dir: Optional[str],
    s3_url: Optional[str],
    s3_bucket: Optional[str],
    s3_access_key_id: Optional[str],
    s3_secret_access_key: Optional[str],
    mirrored: bool = False,
) -> Storage:
    # TODO: after transition from file system to s3, allow only a single storage option
    if (
        s3_url is not None
        and s3_bucket is not None
        and s3_access_key_id is not None
        and s3_secret_access_key is not None
    ):
        s3_storage = S3Storage(s3_url, s3_bucket, s3_access_key_id, s3_secret_access_key)
        if data_dir is not None:
            file_system_storage = FileSystemStorage(data_dir)
            if mirrored:
                storage: Storage = MirroredStorage(s3_storage, file_system_storage)
            else:
                storage = ChainedStorage(s3_storage, file_system_storage)
        else:
            storage = s3_storage
    elif data_dir is not None:
        storage = FileSystemStorage(data_dir)
    else:
        raise click.UsageError(
            "Either --data-dir or all S3 options (--s3-url, --s3-bucket, "
            "--s3-access-key-id, and --s3-secret-access-key) must be provided."
        )

    storage.validate()
    logger.info("Using storage backend: %r", storage)
    return storage
