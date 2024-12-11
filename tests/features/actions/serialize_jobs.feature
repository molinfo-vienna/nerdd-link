Feature: Serialize job action
  Scenario: Serialize valid job
    Given a temporary data directory
    And a list of 100 random molecules
    And a file 'sources/456' with the molecules in format 'sdf'
    
    # process job action
    And the checkpoint size is 40
    And the maximum number of molecules is 10000

    # predict checkpoint action
    And the mol weight model (version 'mol_ids')

    When the channel receives a message on topic 'jobs' with content
        { "id": "123", "job_type": "mol-scale", "source_id": "456", "params": { "multiplier": 10 } }
    And the process job action is executed
    And the predict checkpoints action is executed
    And the channel receives a message on topic 'mol-scale-serialization-requests' with content
        { "job_id": "123", "params": { "multiplier": 10 }, "output_format": "sdf" }
    And the serialize job action is executed

    Then the file 'jobs/123/outputs/result.sdf' is created
