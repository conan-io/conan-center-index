
Feature: This is a doc string example

  Scenario: Doc string with quotes
    When There is a doc string:
    """
    This is a docstring with quotes
    after a step
    """

  Scenario: Doc string with backticks
    When There is a doc string:
    ```
    This is a docstring with backticks
    after a step
    ```
  Scenario: Doc string as vector 
    When There is a doc string as vector:
    """
    This is a docstring 
    which we access 
    as std::vector<std::string>
    """
