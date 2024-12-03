Feature: Register module action

  Scenario: Register a valid module
    Given the mol weight model (version 'mol_ids')

    # note: the content of the system message is irrelevant
    When the channel receives a message on topic 'system' with content
        { "action-type": "init" }
    And the register module action is executed

    Then the channel sends 1 messages on topic 'modules'
    And the channel sends a message on topic 'modules' containing 
        {
            "name": "mol_scale", 
            "version": "0.1", 
            "description": "Computes the molecular weight of a molecule", 
        }