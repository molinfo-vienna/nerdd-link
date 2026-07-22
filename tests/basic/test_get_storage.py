from nerdd_link import FileSystemStorage
from nerdd_link.cli.get_storage import get_storage


def test_validates_before_returning(mocker, tmp_path):
    validate = mocker.patch.object(FileSystemStorage, "validate")

    get_storage(str(tmp_path), None, None, None, None)

    validate.assert_called_once_with()
