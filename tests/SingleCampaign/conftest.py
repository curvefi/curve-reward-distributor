import pytest


@pytest.fixture(scope="module")
def reward_token(project, alice, bob):
    reward_token = alice.deploy(project.TestToken)
    # mint token to bob
    reward_token.mint(bob, 10**19, sender=alice)
    reward_token.mint(bob, 10**18, sender=alice)
    reward_token.approve(bob, 10**19, sender=bob)
    balance = reward_token.balanceOf(bob)
    print(balance)
    return reward_token


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
def single_campaign(project, alice, bob, charlie, crvusd_token):
    # Deploy with bob and charlie as guards
    # Add crvUSD token address and execute_reward_amount parameters
    execute_reward_amount = 10**18  # 1 token as reward
    # Send crvUSD tokens to contract for execute rewards

    contract = alice.deploy(
        project.SingleCampaign, [bob, charlie], crvusd_token, execute_reward_amount
    )
    return contract


@pytest.fixture(scope="module")
def distributor(project, alice, bob, charlie, diana, reward_token, test_gauge, single_campaign):
    # bob guard address
    # diana is recovery address
    print(single_campaign)
    distributor_contract = alice.deploy(
        project.Distributor, [bob, charlie], [single_campaign], reward_token, [test_gauge], diana
    )
    reward_token.approve(distributor_contract, 10**19, sender=bob)
    print(distributor_contract)

    amount = 10**19
    reward_token.transfer(distributor_contract, amount, sender=bob)

    return distributor_contract


@pytest.fixture(scope="module")
def proxy(project, alice):
    # Deploy proxy contract
    proxy_contract = alice.deploy(project.Proxy)
    return proxy_contract
