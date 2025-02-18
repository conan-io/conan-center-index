

Feature: Custom Parameters

  Scenario: An example 
    When this is var1=123, var2=99
    Then their values are 123 and 99

  Scenario: Public Festival 
    When 'The public festival in town' is from April 25, 2025 to Mai 13, 2025
    Then The beginning month is April and the ending month is Mai

  Scenario: Christmas market  
    When 'Christmas Market in Augsburg' is from November 25, 2024 to December 24, 2024
    Then The beginning month is November and the ending month is December
