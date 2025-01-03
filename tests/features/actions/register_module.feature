Feature: Register module action

  Scenario: Register a valid module
    Given a temporary data directory
    And the mol weight model (version 'mol_ids')

    # note: the content of the system message is irrelevant
    When the channel receives a message on topic 'system' with content
        { "action-type": "init" }
    And the register module action is executed

    Then the channel sends 1 messages on topic 'modules'
    And the channel sends a message on topic 'modules' with content
        {
            "id": "mol-scale",
        }
    And the file 'modules/mol-scale' is created