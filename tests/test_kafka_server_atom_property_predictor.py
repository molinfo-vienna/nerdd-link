import pytest
from pytest_bdd import given, parsers, scenario, then
from rdkit.Chem import MolFromSmiles


@scenario(
    "features/kafka_server.feature",
    "Processing input molecules using an atom property predictor",
)
def test_kafka_server_processing():
    pass


@given("the number of expected results", target_fixture="expected_number_of_results")
def expected_number_of_results(input_batches):
    # one result per molecule
    num_mol_entries = sum(len(batch) for batch in input_batches)

    # one result per atom (of valid molecules)
    num_atom_entries = sum(
        MolFromSmiles(entry["raw_input"]).GetNumAtoms()
        for batch in input_batches
        for entry in batch
        if entry["raw_input"] is not None
    )

    return num_mol_entries + num_atom_entries


@then("the prediction response contains one tuple for each molecule")
def check_response_covers_all_molecules(input_batches, prediction_response):
    expected_entries = range(sum(len(batch) for batch in input_batches))

    actual_entries = [
        entry["mol_id"]
        for entry in prediction_response
        if "atom_id" not in entry and "derivative_id" not in entry
    ]

    assert set(expected_entries) == set(actual_entries)


@then("the prediction response contains the prediction results from the model")
def check_prediction_response(predictions, prediction_response):
    for r in prediction_response:
        if "atom_id" in r:
            atom_id = int(r["atom_id"])
            mol_id = r["mol_id"]

            assert (
                r["mass"]
                == predictions[
                    predictions.atom_id.eq(atom_id) & predictions.mol_id.eq(mol_id)
                ].iloc[0]["mass"]
            )


@then("the prediction response contains no atom entries for the None molecules")
def check_response_contains_no_atom_entries_for_none_molecules(
    input_batches, prediction_response
):
    mol_ids_of_none_molecules = [
        entry["mol_id"]
        for batch in input_batches
        for entry in batch
        if entry["raw_input"] is None
    ]

    assert (
        len(
            [
                entry
                for entry in prediction_response
                if entry["mol_id"] in mol_ids_of_none_molecules and "atom_id" in entry
            ]
        )
        == 0
    )
