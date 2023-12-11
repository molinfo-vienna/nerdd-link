@then("the image column should contain svg images")
def check_image_column(subset):
    if len(subset) > 0:
        # check that all images start and end with svg tags
        assert subset.image.str.strip().str.startswith("<svg version='1.1'").all()
        assert subset.image.str.strip().str.endswith("</svg>").all()


@then("the image column should contain svg images")
def check_image_column(subset):
    # check that all images start and end with svg tags
    if len(subset) > 0:
        assert subset.image.str.strip().str.startswith("<svg version='1.1'").all()
        assert subset.image.str.strip().str.endswith("</svg>").all()


@given(
    parsers.parse(
        "the molecules as {input_type} partitioned in {num_partitions:d} batch(es)"
    ),
    target_fixture="input_batches",
)
def input_batches(representations, input_type, multiplier, num_partitions):
    split_indices = np.random.choice(
        len(representations), size=num_partitions - 1, replace=True
    )
    split_indices = sorted(split_indices)

    return np.split(
        [
            {
                "job_id": "abc",
                "job_type": "dummy",
                "mol_id": i,
                "input_type": input_type,
                "raw_input": mol,
                "params": {"multiplier": multiplier},
            }
            for i, mol in enumerate(representations)
        ],
        split_indices,
    )
