from nerdd_link import ChainedStorage, FileSystemStorage


def test_repr():
    first = FileSystemStorage("/path/1")
    second = FileSystemStorage("/path/2")

    storage = ChainedStorage(first, second)

    assert repr(storage) == (
        "ChainedStorage(FileSystemStorage('/path/1'), FileSystemStorage('/path/2'))"
    )


def test_validation_validates_every_child(mocker, tmp_path):
    first = FileSystemStorage(str(tmp_path / "first"))
    second = FileSystemStorage(str(tmp_path / "second"))
    first_validate = mocker.spy(first, "validate")
    second_validate = mocker.spy(second, "validate")

    ChainedStorage(first, second).validate()

    first_validate.assert_called_once_with()
    second_validate.assert_called_once_with()
