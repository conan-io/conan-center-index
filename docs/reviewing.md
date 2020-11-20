# Reviewing policies

The following policies are preferred during the review, but not mandatory:

## Trailing white-spaces

Avoid trailing white-space characters, if possible

## Quotes

If possible, try to avoid mixing single quotes (`'`) over double quotes (`"`) in python code (`conanfile.py`, `test_package/conanfile.py`). Consistency in preferred.

## Order of methods and attributes

Prefer alfa-numeric order of methods in python code (`conanfile.py`, `test_package/conanfile.py`), for instance, `configure` method should go before `package_info` method.
