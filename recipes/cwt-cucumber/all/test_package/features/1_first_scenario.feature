Feature: My first feature
  This is my cucumber-cpp hello world

   Scenario: First Scenario
    Given An empty box
    When I place 1 x "apple" in it
    Then The box contains 1 item
    
  Scenario: Alternative Words 
    Given An empty box
    When I place 1 x "banana" in it
    Then 1 item is "banana" 
    And I place 1 x "banana" in it 
    Then 2 items are "banana" 
