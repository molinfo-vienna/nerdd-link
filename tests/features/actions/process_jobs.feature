Feature: Process job action

  Scenario: Process a valid job
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
    And the process job action is executed

    # files
    Then the file 'jobs/123/inputs/checkpoint_0.pickle' is created
    And the file 'jobs/123/inputs/checkpoint_1.pickle' is created
    And the file 'jobs/123/inputs/checkpoint_2.pickle' is created

    # channel
    And the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 0, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 1, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 2, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'logs' with content 
        { "job_id": "123", "message_type": "report_job_size", "num_entries": 100, "num_checkpoints": 3 }

  Scenario: Process a job with too many molecules
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
            "max_num_molecules": 10,
            "checkpoint_size": 100
        }
    And the process job action is executed

    # files
    Then the file 'jobs/123/inputs/checkpoint_0.pickle' is created

    # channel
    And the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 0, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'logs' with content 
        { "job_id": "123", "message_type": "report_job_size", "num_entries": 10, "num_checkpoints": 1 }
    And the channel sends a message on topic 'logs' with content 
        { 
            "job_id": "123", 
            "message_type": "warning", 
            "message": "The provided job contains more than 10 input structures. Only the first 10 will be processed." 
        }
    
    