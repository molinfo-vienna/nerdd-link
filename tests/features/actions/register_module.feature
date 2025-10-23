Feature: Register module action

  Scenario: Register a valid module
    Given a temporary data directory
    And the mol weight model (version 'mol_ids')

    When the prediction server is running

    Then the channel sends 1 messages on topic 'modules'
    And the channel sends a message on topic 'modules' with content
        {
            "id": "mol-scale",
        }
    And the file 'modules/mol-scale' is created