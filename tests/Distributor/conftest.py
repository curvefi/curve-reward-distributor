import pytest


@pytest.fixture(scope="module")
def reward_token(project, alice, bob):
    reward_token = alice.deploy(project.TestToken)
    # mint token to bob
    reward_token.mint(bob, 10**19, sender=alice)
    reward_token.approve(bob, 10**19, sender=bob)
    balance = reward_token.balanceOf(bob)
    print(balance)
    return reward_token


@pytest.fixture(scope="module")
def lost_token(project, alice, charlie):
    lost_token = alice.deploy(project.TestToken)
    # mint token to charlie
    lost_token.mint(charlie, 10**19, sender=alice)
    lost_token.approve(charlie, 10**19, sender=charlie)
    balance = lost_token.balanceOf(charlie)
    print(balance)
    return lost_token


@pytest.fixture(scope="module")
def test_gauge(project, alice, charlie, diana, reward_token):
    # bob guard address
    # diana is recovery address
    gauge = alice.deploy(project.TestGauge, reward_token, diana)
    return gauge

@pytest.fixture(scope="module")
def test_passthrough(project, alice, charlie, bob, diana, reward_token):
    # bob/charly guard address
    # diana is recovery address
    '''
    def __init__(
    _non_removable_guards: address[3],
    _reward_receivers: DynArray[address, 10],
    _guards: DynArray[address, 6],
    _distributors: DynArray[address, 10],
    ):
    '''
    test_passthrough = alice.deploy(
        project.TestPassthrough, [bob, charlie, diana], [], [], []
    )
    return test_passthrough


@pytest.fixture(scope="module")
def distributor_contract(project, alice, bob, charlie, diana, effi, reward_token, test_gauge, test_passthrough):
    # bob / charlie guard address
    # diana is recovery address
    distributor_contract = alice.deploy(
        project.Distributor, [bob, charlie], [effi], reward_token, [test_gauge, test_passthrough], diana
    )
    reward_token.approve(distributor_contract, 10**19, sender=bob)
    return distributor_contract


