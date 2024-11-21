Feature: Register module action

  Scenario: Register a valid module
    Given a mocked cummunication channel
    And the mol weight model (version 'mol_ids')

    # note: the content of the system message is irrelevant
    When the channel receives a message on topic 'system' with content
        { "action-type": "init" }
    And the register module action is executed

    Then the channel sends 1 messages on topic 'modules'
    # Then the channel sends a message on topic 'modules' with content 
    #     {
    #         "name": "mol_scale", 
    #         "version": "0.1", 
    #         "description": "Computes the molecular weight of a molecule", 
    #         "result_properties": [
    #             {'name': 'mol_id', 'type': 'integer'}, 
    #             {'name': 'raw_input', 'type': 'string'}, 
    #             {'name': 'input_type', 'type': 'string'}, 
    #             {'name': 'source'}, 
    #             {'name': 'name', 'type': 'string'}, 
    #             {'name': 'input_mol', 'type': 'mol'}, 
    #             {'name': 'preprocessed_mol', 'type': 'mol'}, 
    #             {'name': 'weight', 'type': 'float'}, 
    #             {'name': 'problems', 'type': 'problem_list'}
    #         ],
    #         "job_parameters": [
    #             {'name': 'multiplier', 'type': 'float'}
    #         ] 
    #     }