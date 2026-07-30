import logging
from typing import Literal, Optional

import rich_click as click

from ..storage import ChainedStorage, FileSystemStorage, MirroredStorage, S3Storage, Storage

__all__ = ["get_storage"]

logger = logging.getLogger(__name__)

StorageMode = Literal["mirrored", "chained", "single"]


def get_storage(
    data_dir: Optional[str],
    s3_url: Optional[str],
    s3_bucket: Optional[str],
    s3_access_key_id: Optional[str],
    s3_secret_access_key: Optional[str],
    mode: StorageMode = "single",
) -> Storage:
    # create potential storages from CLI arguments
    storages: list[Storage] = []
    if (
        s3_url is not None
        and s3_bucket is not None
        and s3_access_key_id is not None
        and s3_secret_access_key is not None
    ):
        storages.append(S3Storage(s3_url, s3_bucket, s3_access_key_id, s3_secret_access_key))
    if data_dir is not None:
        storages.append(FileSystemStorage(data_dir))

    # to avoid confusion, fail if a portion of S3 options are provided
    s3_options = (s3_url, s3_bucket, s3_access_key_id, s3_secret_access_key)
    any_s3_options_provided = any(option is not None for option in s3_options)
    all_s3_options_provided = all(option is not None for option in s3_options)
    if any_s3_options_provided and not all_s3_options_provided:
        raise click.UsageError(
            "A subset of S3 options (--s3-url, --s3-bucket, --s3-access-key-id, and "
            "--s3-secret-access-key) were provided. Please provide either none or all S3 options."
        )

    if len(storages) == 0:
        raise click.UsageError(
            "At least --data-dir or all S3 options (--s3-url, --s3-bucket, "
            "--s3-access-key-id, and --s3-secret-access-key) must be provided."
        )

    # construct specified storage backend
    if mode == "single":
        if len(storages) > 1:
            raise click.UsageError(
                "The application accepts only one storage backend. Please provide either "
                "--data-dir or all S3 options (--s3-url, --s3-bucket, --s3-access-key-id, and "
                "--s3-secret-access-key)."
            )
        else:
            storage = storages[0]
    elif mode == "mirrored":
        storage = MirroredStorage(*storages)
    elif mode == "chained":
        storage = ChainedStorage(*storages)
    else:
        raise ValueError(
            f"Invalid storage mode: {mode}. Must be one of 'single', 'mirrored', or 'chained'."
        )

    storage.validate()
    logger.info("Using storage backend: %r", storage)
    return storage
