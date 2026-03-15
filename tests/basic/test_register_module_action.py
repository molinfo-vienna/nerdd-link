import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from nerdd_link.actions import RegisterModuleAction
from nerdd_link.channels.memory_channel import MemoryChannel
from nerdd_link.storage import FileSystemStorage
from nerdd_link.types import SystemMessage


@pytest.fixture
def registration(tmp_path):
    config = Mock(id="example")
    config.model_dump.return_value = {"id": "example", "name": "Example"}
    channel = MemoryChannel()
    storage = FileSystemStorage(str(tmp_path))
    action = RegisterModuleAction(channel, SimpleNamespace(config=config), storage)
    return action, channel, storage, config.model_dump.return_value


@pytest.mark.asyncio
@pytest.mark.parametrize("existing", [None, {"id": "example", "name": "Old"}])
async def test_registration_persists_and_announces_new_or_changed_config(registration, existing):
    action, channel, storage, config = registration
    if existing is not None:
        with storage.get_module_file_handle("example", "w") as f:
            json.dump(existing, f)

    async with channel:
        await action.register()

    with storage.get_module_file_handle("example", "r") as f:
        assert json.load(f) == config
    assert channel.get_produced_messages() == [("modules", ("example",), {"id": "example"})]


@pytest.mark.asyncio
@pytest.mark.parametrize("initialize", [False, True])
async def test_unchanged_config_is_only_announced_on_initialization(
    registration, mocker, initialize
):
    action, channel, storage, config = registration
    with storage.get_module_file_handle("example", "w") as f:
        json.dump(config, f)
    handles = mocker.spy(storage, "get_module_file_handle")

    async with channel:
        if initialize:
            await action._process_message(SystemMessage())
        else:
            await action.register()

    handles.assert_called_once_with("example", "r")
    expected = [("modules", ("example",), {"id": "example"})] if initialize else []
    assert channel.get_produced_messages() == expected


@pytest.mark.asyncio
async def test_storage_failure_prevents_announcement(registration, mocker):
    action, channel, storage, _ = registration
    mocker.patch.object(storage, "get_module_file_handle", side_effect=OSError("write failed"))

    async with channel:
        with pytest.raises(OSError, match="write failed"):
            await action.register(force_announce=True)

    assert channel.get_produced_messages() == []


@pytest.mark.asyncio
async def test_failed_announcement_can_be_recovered_by_initialization(registration, mocker):
    action, channel, _, _ = registration
    send = mocker.patch.object(channel, "_send", new_callable=AsyncMock)
    send.side_effect = RuntimeError("publication failed")

    async with channel:
        with pytest.raises(RuntimeError, match="publication failed"):
            await action.register()

        send.reset_mock(side_effect=True)
        await action.register()
        send.assert_not_awaited()

        await action._process_message(SystemMessage())
        send.assert_awaited_once()
