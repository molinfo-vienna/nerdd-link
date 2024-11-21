Feature: Process job action

  Scenario: Process a valid job
    Given the data directory is a temporary directory
    And a list of 100 random molecules, where 0 entries are None
    And a file 'sources/456' with the molecules in format 'sdf'
    
    And the checkpoint size is 40
    And the maximum number of molecules is 10000
    And a mocked cummunication channel

    When the channel receives a message on topic 'jobs' with content
        { "id": "123", "job_type": "mol-scale", "source_id": "456", "params": { "multiplier": 10 } }
    And the process job action is executed

    Then the file 'jobs/123/input/checkpoint_0.pickle' is created
    And the file 'jobs/123/input/checkpoint_1.pickle' is created
    And the file 'jobs/123/input/checkpoint_2.pickle' is created
    And the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 0, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 1, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 2, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'logs' with content 
        { "job_id": "123", "message_type": "report_job_size", "size": 100 }

  Scenario: Process a job with too many molecules
    Given the data directory is a temporary directory
    And a list of 100 random molecules, where 0 entries are None
    And a file 'sources/456' with the molecules in format 'sdf'
    
    And the checkpoint size is 100
    And the maximum number of molecules is 10
    And a mocked cummunication channel

    When the channel receives a message on topic 'jobs' with content
        { "id": "123", "job_type": "mol-scale", "source_id": "456", "params": { "multiplier": 10 } }
    And the process job action is executed

    Then the file 'jobs/123/input/checkpoint_0.pickle' is created
    And the channel sends a message on topic 'mol-scale-checkpoints' with content 
        { "job_id": "123", "checkpoint_id": 0, "params": { "multiplier": 10 } }
    And the channel sends a message on topic 'logs' with content 
        { "job_id": "123", "message_type": "report_job_size", "size": 10 }
    And the channel sends a message on topic 'logs' with content 
        { 
            "job_id": "123", 
            "message_type": "warning", 
            "message": "The provided job contains more than 10 input structures. Only the first 10 will be processed." 
        }
    
    