Feature: Serialize job action
  Scenario: Serialize valid job
    Given a temporary data directory
    And a list of 100 random molecules
    And a file 'sources/456' with the molecules in format 'sdf'
    And the mol weight model (version 'mol_ids')

    # start all participating servers
    When the prediction server is running
    And the job server is running
    And the serialization server is running

    # predict checkpoint action    
    And the channel receives a message on topic 'jobs' with content
        { 
            "id": "123", 
            "job_type": 
            "mol-scale", 
            "source_id": "456", 
            "params": { "multiplier": 10 },
            "max_num_molecules": 10000,
            "checkpoint_size": 40
        }
    And we wait for 1 seconds
    And the channel receives a message on topic 'serialization-requests' with content
        { "job_id": "123", "job_type": "mol-scale", "params": { "multiplier": 10 }, "output_format": "sdf" }
    And we wait for 1 seconds

    Then the file 'jobs/123/outputs/result.sdf' is created
    And the channel sends a message on topic 'serialization-results' with content
        { "job_id": "123", "output_format": "sdf" }
