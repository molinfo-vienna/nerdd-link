from typing import Optional

from ..storage import FileSystemStorage, Storage

__all__ = ["get_storage"]


def get_storage(
    data_dir: Optional[str],
    s3_url: Optional[str],
    s3_bucket: Optional[str],
    s3_username: Optional[str],
    s3_password: Optional[str],
) -> Storage:
    if data_dir is None:
        raise ValueError("data_dir must be provided.")

    return FileSystemStorage(data_dir)
