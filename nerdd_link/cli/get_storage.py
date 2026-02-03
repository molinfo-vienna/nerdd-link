from typing import Optional

from ..storage import FileSystemStorage, Storage

__all__ = ["get_storage"]


def get_storage(
    data_dir: str,
    s3_bucket: Optional[str],
    s3_username: Optional[str],
    s3_password: Optional[str],
) -> Storage:
    return FileSystemStorage(data_dir)
