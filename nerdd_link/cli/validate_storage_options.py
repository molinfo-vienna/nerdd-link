from typing import Optional

import rich_click as click

__all__ = ["validate_storage_options"]


def validate_storage_options(
    data_dir: Optional[str],
    s3_url: Optional[str],
    s3_bucket: Optional[str],
    s3_username: Optional[str],
    s3_password: Optional[str],
) -> None:
    s3_options = (s3_url, s3_bucket, s3_username, s3_password)
    if data_dir is not None or all(option is not None for option in s3_options):
        return

    raise click.UsageError(
        "Either --data-dir or all S3 options (--s3-url, --s3-bucket, "
        "--s3-username, and --s3-password) must be provided."
    )
