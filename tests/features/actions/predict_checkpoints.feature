Feature: Predict checkpoints action
  Scenario: Process valid checkpoints
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
    And we wait for 2 seconds

    # files
    Then the file 'jobs/123/results/checkpoint_0.pickle' is created
    And the file 'jobs/123/results/checkpoint_1.pickle' is created
    And the file 'jobs/123/results/checkpoint_2.pickle' is created

    # channels
    # actions sends result messages:
    And the channel sends 100 messages on topic 'results'
    # actions sends result checkpoint messages:
    And the channel sends a message on topic 'result-checkpoints' with content
        { "job_id": "123", "checkpoint_id": 0 }
    And the channel sends a message on topic 'result-checkpoints' with content
        { "job_id": "123", "checkpoint_id": 1 }
    And the channel sends a message on topic 'result-checkpoints' with content
        { "job_id": "123", "checkpoint_id": 2 }
