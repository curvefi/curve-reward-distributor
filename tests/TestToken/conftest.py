import pytest


@pytest.fixture(scope="module")
def reward_token(project, alice, bob):
    token = alice.deploy(project.TestToken)
    token.mint(bob, 1000000 * 10**18, sender=alice)
    return token
