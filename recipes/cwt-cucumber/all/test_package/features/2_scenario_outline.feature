
Feature: My first feature
  This is my cucumber-cpp hello world

  Scenario Outline: First Scenario Outline
    Given An empty box
    When I place <count> x <item> in it
    Then The box contains <count> items

    Examples:
      | count | item      |
      | 1     | "apple"   |
      | 2     | "bananas" |

  Scenario Outline: a scenario outline  
    When A <word> and <anonymous>
    Then They will match <expected word> and <expected anonymous>
    
    Examples:
      | word      | anonymous | expected word | expected anonymous |
      | 123.123   | -999.9999 | "123.123"     | "-999.9999"        | 
      | -123,123  | -999,9999 | "-123,123"    | "-999,9999"        | 
      | "abc"     | -999,9999 | ""abc""       | "-999,9999"        | 
      | abc       | -00:00,00 | "abc"         | "-00:00,00"        | 


  Scenario Outline: lets put the quotes in the step ...  
    When A <word> and <anonymous>
    Then They will match "<expected word>" and "<expected anonymous>"
    
    Examples:
      | word      | anonymous | expected word | expected anonymous |
      | 123.123   | -999.    9999 | 123.123       | -999.    9999          | 
      | "abc"     | -00:00,00 | "abc"         | -00:00,00          | 



