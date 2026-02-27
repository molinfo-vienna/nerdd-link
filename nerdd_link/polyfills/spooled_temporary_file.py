import sys
from tempfile import SpooledTemporaryFile as _SpooledTemporaryFile

__all__ = ["SpooledTemporaryFile"]


if sys.version_info >= (3, 11):
    SpooledTemporaryFile = _SpooledTemporaryFile
else:

    class SpooledTemporaryFile(_SpooledTemporaryFile):
        """A ``SpooledTemporaryFile`` compatible with Python's IO wrappers.

        Python versions before 3.11 do not expose the capability methods
        required by wrappers such as :class:`io.TextIOWrapper`.
        """

        def readable(self) -> bool:
            return not self.closed

        def writable(self) -> bool:
            return not self.closed

        def seekable(self) -> bool:
            return not self.closed
