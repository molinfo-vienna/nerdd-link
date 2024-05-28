import numpy as np
from pytest_bdd import given, parsers
from rdkit.Chem import MolToInchi, MolToMolBlock, MolToSmiles


@given(
    parsers.parse('the records of the molecules in "{input_type}" format'),
    target_fixture="records",
)
def records(molecules, input_type, multiplier):
    def _record(i, mol):
        # convert to representation
        if input_type == "smiles":
            converter = MolToSmiles
        elif input_type == "mol_block":
            converter = MolToMolBlock
        elif input_type == "inchi":
            converter = MolToInchi
        else:
            raise ValueError(f"Unknown input_type: {input_type}")

        if mol is None:
            representation = None
        else:
            representation = converter(mol)

        return {
            "job_id": "abc",
            "job_type": "dummy",
            "mol_id": i,
            "input_type": input_type,
            "raw_input": representation,
            "source": ("test.file"),
            "errors": [],
            "params": {"multiplier": multiplier},
        }

    return [_record(i, mol) for i, mol in enumerate(molecules)]


@given(
    parsers.parse("the records partitioned in {num_partitions:d} batch(es)"),
    target_fixture="input_batches",
)
def input_batches(records, num_partitions):
    split_indices = np.random.choice(
        len(records), size=num_partitions - 1, replace=True
    )
    split_indices = sorted(split_indices)

    return np.split(
        records,
        split_indices,
    )
