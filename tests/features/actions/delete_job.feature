Feature: Delete job

  Scenario: Delete valid after prediction
    Given a temporary data directory
    And a list of 100 random molecules
    And a file 'sources/456' with the molecules in format 'sdf'

    # predict checkpoint action
    And the mol weight model (version 'mol_ids')
    
    #
    # First, job is processed normally
    #
    When the channel receives a message on topic 'jobs' with content
        { 
            "id": "123", 
            "job_type": 
            "mol-scale", 
            "source_id": "456", 
            "params": { "multiplier": 10 },
            "max_num_molecules": 10000,
            "checkpoint_size": 40
        }
    And the process job action is executed
    And the predict checkpoints action is executed

    Then the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 0, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 1, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 2, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'logs' with content 
        { "job_id": "123", "message_type": "report_job_size", "num_entries": 100, "num_checkpoints": 3 }

    #
    # Then, job is deleted
    #
    When the channel receives a tombstone on topic 'jobs' with key ("123", "mol-scale")
    And we wait for 1 seconds

    # files
    Then the file 'jobs/123/inputs/checkpoint_0.pickle' does not exist
    And the file 'jobs/123/inputs/checkpoint_1.pickle' does not exist
    And the file 'jobs/123/inputs/checkpoint_2.pickle' does not exist

    And the file 'jobs/123/results/checkpoint_0.pickle' does not exist
    And the file 'jobs/123/results/checkpoint_1.pickle' does not exist
    And the file 'jobs/123/results/checkpoint_2.pickle' does not exist

    # channel
    And the channel sends a tombstone on topic 'mol-scale-checkpoints' with key ("123", 0)
    And the channel sends a tombstone on topic 'mol-scale-checkpoints' with key ("123", 1)
    And the channel sends a tombstone on topic 'mol-scale-checkpoints' with key ("123", 2)

    And the channel sends a tombstone on topic 'result-checkpoints' with key ("123", 0)
    And the channel sends a tombstone on topic 'result-checkpoints' with key ("123", 1)
    And the channel sends a tombstone on topic 'result-checkpoints' with key ("123", 2)


  Scenario: Delete job before prediction
    Given a temporary data directory
    And a list of 100 random molecules
    And a file 'sources/456' with the molecules in format 'sdf'

    # predict checkpoint action
    And the mol weight model (version 'mol_ids')
    
    #
    # Job is processed, but checkpoints are not predicted
    #
    When the channel receives a message on topic 'jobs' with content
        { 
            "id": "123", 
            "job_type": 
            "mol-scale", 
            "source_id": "456", 
            "params": { "multiplier": 10 },
            "max_num_molecules": 10000,
            "checkpoint_size": 40
        }
    And the process job action is executed

    Then the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 0, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 1, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 2, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'logs' with content 
        { "job_id": "123", "message_type": "report_job_size", "num_entries": 100, "num_checkpoints": 3 }

    #
    # Then, job is deleted
    #
    When the channel receives a tombstone on topic 'jobs' with key ("123", "mol-scale")
    And the predict checkpoints action is executed
    And we wait for 1 seconds

    # files
    Then the file 'jobs/123/inputs/checkpoint_0.pickle' does not exist
    And the file 'jobs/123/inputs/checkpoint_1.pickle' does not exist
    And the file 'jobs/123/inputs/checkpoint_2.pickle' does not exist

    And the file 'jobs/123/results/checkpoint_0.pickle' does not exist
    And the file 'jobs/123/results/checkpoint_1.pickle' does not exist
    And the file 'jobs/123/results/checkpoint_2.pickle' does not exist

    # channel
    And the channel sends a tombstone on topic 'mol-scale-checkpoints' with key ("123", 0)
    And the channel sends a tombstone on topic 'mol-scale-checkpoints' with key ("123", 1)
    And the channel sends a tombstone on topic 'mol-scale-checkpoints' with key ("123", 2)
    # note: no result checkpoints are sent, because they were never predicted


  Scenario: Delete job twice
    Given a temporary data directory
    And a list of 100 random molecules
    And a file 'sources/456' with the molecules in format 'sdf'
    
    When the channel receives a message on topic 'jobs' with content
        { 
            "id": "123", 
            "job_type": 
            "mol-scale", 
            "source_id": "456", 
            "params": { "multiplier": 10 },
            "max_num_molecules": 10000,
            "checkpoint_size": 40
        }
    And the channel receives a tombstone on topic 'jobs' with key ("123", "mol-scale")
    And the channel receives a tombstone on topic 'jobs' with key ("123", "mol-scale")
    # The following line is important now: it should not cause an error for the second tombstone
    And the process job action is executed

    # Check that tombstones were sent at least once (twice would be fine)
    Then the channel sends a tombstone on topic 'mol-scale-checkpoints' with key ("123", 0)
    And the channel sends a tombstone on topic 'mol-scale-checkpoints' with key ("123", 1)
    And the channel sends a tombstone on topic 'mol-scale-checkpoints' with key ("123", 2)