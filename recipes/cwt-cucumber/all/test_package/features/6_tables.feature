
Feature: This represents tables
  We have three options:
  - raw access
  - rows hash
  - key/value pairs

  Scenario: Adding items with raw
    Given An empty box
    When I add all items with the raw function:
      | apple      | 2 |
      | strawberry | 3 |
      | banana     | 5 |
    Then The box contains 10 items

  Scenario: Adding items with hashes
    Given An empty box
    When I add all items with the hashes function:
      | ITEM   | QUANTITY |
      | apple  | 3        |
      | banana | 6        |
    Then The box contains 9 items


  Scenario: Adding items with rows_hash
    Given An empty box
    When I add the following item with the rows_hash function:
      | ITEM     | really good apples |
      | QUANTITY | 3                  |
    Then The box contains 3 items

