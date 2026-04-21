from nerdd_link import Channel


def test_get_channel_names():
    # make sure that "kafka" is a valid channel name
    assert "kafka" in Channel.get_channel_names()
