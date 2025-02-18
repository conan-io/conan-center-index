Feature: Scenarios with tags

  @ship 
  Scenario: We want to ship cucumbers
    Given An empty box
    When I place 1 x "cucumber" in it
    Then The box contains 1 item

  @important
  Scenario: Important items must be shipped immediately
    Given An empty box
    When I place 2 x "important items" in it
    Then The box contains 2 items