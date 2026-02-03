__all__ = ["WrongPrefixError"]


class WrongPrefixError(ValueError):
    def __init__(self, expected_prefix: str, file_path: str) -> None:
        self.expected_prefix = expected_prefix
        self.file_path = file_path
        super().__init__(
            f"Expected file path to start with '{expected_prefix}://', got '{file_path}'."
        )
