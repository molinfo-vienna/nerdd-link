from nerdd_module.input import Reader
from nerdd_module.output import Writer

import nerdd_link


def test_plugin_registers_input_and_output_classes() -> None:
    from nerdd_link.input import StructureJsonReader

    assert StructureJsonReader in Reader.get_reader_mapping()
    assert {"json", "pickle"}.issubset(Writer.get_output_formats())


def test_plugin_classes_are_not_part_of_the_root_api() -> None:
    assert not hasattr(nerdd_link, "StructureJsonReader")
    assert not hasattr(nerdd_link, "ChannelWriter")
    assert not hasattr(nerdd_link, "PickleWriter")
    assert not hasattr(nerdd_link, "PickleConverter")
