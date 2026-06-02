Automated testing is run via a python module called pytest.

Each function starting with the prefix test\_ is run, and assert statements determine test success.

Tests are run automatically by github actions using the "integration-tests.yml". Pytest can be run manually using the following command:
poetry run pytest
