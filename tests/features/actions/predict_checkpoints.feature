Feature: Predict checkpoints action
  Scenario: Process valid checkpoints
    Given a temporary data directory
    And a list of 100 random molecules
    And a file 'sources/456' with the molecules in format 'sdf'

    # predict checkpoint action
    And the mol weight model (version 'mol_ids')

    # start all participating servers
    When the job server is running
    And the prediction server is running
    
    And the channel receives a message on topic 'jobs' with content
        { "id": "123", 
          "job_type": "mol-scale", 
          "source_id": "456", 
          "params": { "multiplier": 10 }, 
          "max_num_molecules": 10000, 
          "checkpoint_size": 40 
        }
    And we wait for 1 seconds

    # files
    Then the file 'jobs/123/results/checkpoint_0.pickle' is created
    And the file 'jobs/123/results/checkpoint_1.pickle' is created
    And the file 'jobs/123/results/checkpoint_2.pickle' is created

    # channels
    # actions sends result messages:
    And the channel sends 100 messages on topic 'results'
    # actions sends result checkpoint messages:
    And the channel sends a message on topic 'result-checkpoints' containing
        { "job_id": "123", "checkpoint_id": 0 }
    And the channel sends a message on topic 'result-checkpoints' containing
        { "job_id": "123", "checkpoint_id": 1 }
    And the channel sends a message on topic 'result-checkpoints' containing
        { "job_id": "123", "checkpoint_id": 2 }
