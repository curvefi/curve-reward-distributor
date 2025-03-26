import pytest


@pytest.fixture(scope="session")
def alice(accounts):
    return accounts[0]


@pytest.fixture(scope="session")
# guard address
def bob(accounts):
    return accounts[1]


@pytest.fixture(scope="session")
# charlie is backup guard address
# charlie is sends wrong token to reward guard
def charlie(accounts):
    return accounts[2]


@pytest.fixture(scope="session")
# diana is recovery address
def diana(accounts):
    return accounts[3]
