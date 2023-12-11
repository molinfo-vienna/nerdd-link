Feature: Kafka server

  Scenario: Start a server with a model
    Given example model predicting molecular weight, version no_ids
    And no input messages
    And a mocked kafka consumer
    And a mocked kafka producer
    And a kafka server initialized with the model
    
    Then the server sends a configuration message


  Scenario: Processing input molecules using a molecule property predictor
    Given a prediction parameter 'multiplier' set to 3
    And example model predicting molecular weight, version no_ids

    And a list of 10 random molecules, where 5 entries are None
    And the representations of the molecules as smiles
    And the molecules as smiles partitioned in 1 batch(es)
    And a mocked kafka consumer
    And a mocked kafka producer
    And a kafka server initialized with the model

    And the number of expected results

    When the model is used on the molecules given as smiles
    And the server responds


  Scenario: Processing input molecules using an atom property predictor
    Given a prediction parameter 'multiplier' set to 3
    And example model predicting atomic masses, version no_ids
    
    And a list of 10 random molecules, where 5 entries are None
    And the representations of the molecules as smiles
    And the molecules as smiles partitioned in 1 batch(es)
    
    And a mocked kafka consumer
    And a mocked kafka producer
    And a kafka server initialized with the model

    And the number of expected results

    When the model is used on the molecules given as smiles
    And the server responds

    Then the prediction response contains one tuple for each molecule
    And the prediction response contains the prediction results from the model
    And the prediction response contains no atom entries for the None molecules