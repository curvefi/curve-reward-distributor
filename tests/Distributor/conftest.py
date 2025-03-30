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
def crvusd_token(project, alice, charlie):
    crvusd_token = alice.deploy(project.TestToken)
    # mint token to charlie
    crvusd_token.mint(charlie, 10**19, sender=alice)
    crvusd_token.approve(charlie, 10**19, sender=charlie)
    balance = crvusd_token.balanceOf(charlie)
    print(balance)
    return crvusd_token

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
        project.Distributor, [bob, charlie], [], reward_token, [test_gauge, test_passthrough], diana
    )
    reward_token.approve(distributor_contract, 10**19, sender=bob)
    return distributor_contract


@pytest.fixture(scope="module")
def single_campaign(project, alice, bob, charlie, crvusd_token, distributor_contract, test_gauge):
    # Deploy with bob and charlie as guards
    # Add crvUSD token address and execute_reward_amount parameters
    execute_reward_amount = 10**18  # 1 token as reward
    # Send crvUSD tokens to contract for execute rewards

    contract = alice.deploy(
        project.SingleCampaign, [bob, charlie], crvusd_token, execute_reward_amount
    )

    epochs = [1 * 10**18, 2 * 10**18, 3 * 10**18]
    contract.set_reward_epochs(epochs, sender=bob)
    # Setup the reward guard and receiver addresses with 3 day epoch duration
    contract.setup(
        distributor_contract.address, test_gauge.address, 3 * 24 * 60 * 60, 1, "test", sender=charlie
    )

    return contract
