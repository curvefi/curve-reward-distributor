import ape

DAY = 86400
WEEK = 604800


def test_distributor_guards(bob, charlie, distributor_contract):
    assert distributor_contract.guards(0) == bob
    assert distributor_contract.guards(1) == charlie


def test_distributor_reward_token(bob, reward_token, distributor_contract):
    assert distributor_contract.reward_token() == reward_token


def test_distributor_receivers(bob, test_gauge, distributor_contract):
    receiving_gauges = distributor_contract.receiving_gauges(0)
    print(receiving_gauges)
    assert test_gauge == receiving_gauges


# send reward token to reward guard contract, then deposit_reward_tokens
def test_distributor_send_reward_token(alice, bob, diana, reward_token, test_gauge, distributor_contract):
    amount = 10**16
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == 0
    reward_token.transferFrom(bob, distributor_contract, amount, sender=bob)
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == amount
    distributor_contract.send_reward_token(test_gauge, amount, sender=bob)
    assert test_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(diana, sender=alice)
    assert amount == balance_recoverd
    assert amount == distributor_balance


def test_distributor_send_reward_token_epoch(
    alice, bob, diana, reward_token, test_gauge, distributor_contract
):
    amount = 10**16
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == 0
    reward_token.transferFrom(bob, distributor_contract, amount, sender=bob)
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == amount
    distributor_contract.send_reward_token(test_gauge, amount, 8 * DAY, sender=bob)
    assert test_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(diana, sender=alice)
    assert amount == balance_recoverd
    assert amount == distributor_balance


def test_distributor_send_reward_token_active_campaign_addresses(
    alice, bob, diana, reward_token, test_gauge, distributor_contract
):
    amount = 10**16
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == 0
    reward_token.transferFrom(bob, distributor_contract, amount, sender=bob)
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == amount
    distributor_contract.send_reward_token(test_gauge, amount, 8 * DAY, sender=bob)

    assert distributor_contract.active_campaign_addresses(0) == bob
    active_addresses = distributor_contract.get_all_active_campaign_addresses()
    assert active_addresses[0] == bob


def test_distributor_sent_revert(alice, test_gauge, distributor_contract):
    with ape.reverts("only reward guards or campaign contracts can call this function"):
        distributor_contract.send_reward_token(test_gauge, 10**18, sender=alice)


def test_distributor_epoch_revert_too_short(bob, test_gauge, distributor_contract):
    with ape.reverts("epoch duration must be between 3 days and a year"):
        distributor_contract.send_reward_token(test_gauge, 10**18, DAY, sender=bob)


def test_distributor_epoch_revert_too_long(bob, test_gauge, distributor_contract):
    with ape.reverts("epoch duration must be between 3 days and a year"):
        distributor_contract.send_reward_token(test_gauge, 10**18, 53 * WEEK, sender=bob)


def test_recover_token(bob, charlie, diana, lost_token, distributor_contract):
    amount = 10**18
    lost_token.transferFrom(charlie, distributor_contract, amount, sender=charlie)
    assert lost_token.balanceOf(distributor_contract) == amount
    # rest of lost token on charlies address, start with 10 ** 19
    assert lost_token.balanceOf(charlie) == 9 * amount
    # recover lost token to diana (recovery address)
    distributor_contract.recover_token(lost_token, amount, sender=bob)
    assert lost_token.balanceOf(diana) == amount


def test_recover_reward_token(bob, charlie, diana, reward_token, distributor_contract):
    amount = 10**18
    reward_token.transferFrom(bob, distributor_contract, amount, sender=bob)
    assert reward_token.balanceOf(distributor_contract) == amount
    # rest of lost token on charlies address, start with 10 ** 19
    assert reward_token.balanceOf(bob) == 9 * amount
    # recover lost token to diana (recovery address)
    distributor_contract.recover_token(reward_token, amount, sender=bob)
    assert reward_token.balanceOf(diana) == amount


def test_recover_token_revert_manager(alice, lost_token, distributor_contract):
    with ape.reverts("only reward guards can call this function"):
        distributor_contract.recover_token(lost_token, 10**18, sender=alice)


def test_recover_token_revert_amount(bob, lost_token, distributor_contract):
    with ape.reverts("amount must be greater than 0"):
        distributor_contract.recover_token(lost_token, 0, sender=bob)


def test_remove_active_campaign_address(alice, bob, charlie, reward_token, test_gauge, distributor_contract):
    """Test removing active campaign addresses"""
    # First send a reward to add a campaign address
    amount = 10**16
    reward_token.transferFrom(bob, distributor_contract, amount, sender=bob)

    distributor_contract.send_reward_token(test_gauge, amount, sender=bob)

    # Verify active campaign address is in the list
    assert distributor_contract.active_campaign_addresses(0) == bob
    active_addresses = distributor_contract.get_all_active_campaign_addresses()
    print(active_addresses)
    assert active_addresses[0] == bob

    # Remove active campaign address
    distributor_contract.remove_active_campaign_address(bob, sender=bob)

    # Verify active campaign address was removed
    active_addresses = distributor_contract.get_all_active_campaign_addresses()
    print(active_addresses)
    assert len(active_addresses) == 0


def test_remove_active_campaign_address_revert_non_guard(
    alice, bob, reward_token, test_gauge, distributor_contract
):
    """Test that non-guards cannot remove active campaign addresses"""
    # First send a reward to add a campaign address
    amount = 10**16
    reward_token.transferFrom(bob, distributor_contract, amount, sender=bob)
    distributor_contract.send_reward_token(test_gauge, amount, sender=bob)

    with ape.reverts("only reward guards or campaign contracts can call this function"):
        distributor_contract.remove_active_campaign_address(bob, sender=alice)

# Test for the send_reward method that uses passthrough
def test_distributor_passthrough_setup(
    alice, bob, diana, effi, reward_token, test_gauge, test_passthrough, distributor_contract
):
    amount = 10**16
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == 0
    reward_token.transferFrom(bob, distributor_contract, amount, sender=bob)
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == amount

    with ape.reverts("reward token mismatch or single reward token not set"):
        distributor_contract.send_reward(test_passthrough, amount, sender=bob)

    test_passthrough.set_single_reward_token(reward_token, "test reward token", sender=bob)

    with ape.reverts("only reward guards or campaign contracts can call this function"):
        distributor_contract.send_reward(test_passthrough, amount, sender=alice)
    
    test_passthrough.add_distributor(distributor_contract, sender=bob)

    with ape.reverts("single reward receiver not set"):
        distributor_contract.send_reward(test_passthrough, amount, sender=bob)

    test_passthrough.set_single_reward_receiver(test_gauge, sender=bob)

    distributor_contract.send_reward(test_passthrough, amount, sender=bob)

    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == 0


# Test for the send_reward method that uses passthrough
def test_distributor_send_reward(
    alice, bob, diana, effi, reward_token, test_gauge, test_passthrough, distributor_contract
):
    amount = 10**16
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == 0
    reward_token.transferFrom(bob, distributor_contract, amount, sender=bob)
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == amount

    # set up of passthrough
    test_passthrough.add_distributor(distributor_contract, sender=bob)
    test_passthrough.set_single_reward_token(reward_token, "test reward token", sender=bob)
    test_passthrough.set_single_reward_receiver(test_gauge, sender=bob)

    distributor_contract.send_reward(test_passthrough, amount, sender=bob)

    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == 0

    test_gauge_balance = reward_token.balanceOf(test_gauge, sender=alice)
    assert test_gauge_balance == amount


# Test for the send_reward method with custom epoch
def test_distributor_send_reward_epoch(
    alice, bob, diana, reward_token, test_gauge, test_passthrough, distributor_contract
):
    amount = 10**16
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == 0
    reward_token.transferFrom(bob, distributor_contract, amount, sender=bob)
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == amount

    custom_epoch = 8 * DAY

    # set up of passthrough
    test_passthrough.add_distributor(distributor_contract, sender=bob)
    test_passthrough.set_single_reward_token(reward_token, "test reward token", sender=bob)
    test_passthrough.set_single_reward_receiver(test_gauge, sender=bob)

    distributor_contract.send_reward(test_passthrough, amount, custom_epoch, sender=bob)

    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == 0

    test_gauge_balance = reward_token.balanceOf(test_gauge, sender=alice)
    assert test_gauge_balance == amount


# Test that send_reward adds active campaign addresses
def test_distributor_send_reward_active_campaign_addresses(
    alice, bob, diana, reward_token, test_gauge, test_passthrough, distributor_contract
):
    amount = 10**16
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == 0
    reward_token.transferFrom(bob, distributor_contract, amount, sender=bob)
    distributor_balance = reward_token.balanceOf(distributor_contract, sender=alice)
    assert distributor_balance == amount

    # set up of passthrough
    test_passthrough.add_distributor(distributor_contract, sender=bob)
    test_passthrough.set_single_reward_token(reward_token, "test reward token", sender=bob)
    test_passthrough.set_single_reward_receiver(test_gauge, sender=bob)

    distributor_contract.send_reward(test_passthrough, amount, 8 * DAY, sender=bob)

    assert distributor_contract.active_campaign_addresses(0) == bob
    active_addresses = distributor_contract.get_all_active_campaign_addresses()
    assert active_addresses[0] == bob


# Test send_reward permissions
def test_distributor_send_reward_revert(alice, test_passthrough, distributor_contract):
    with ape.reverts("only reward guards or campaign contracts can call this function"):
        distributor_contract.send_reward(test_passthrough, 10**18, sender=alice)


# Test send_reward epoch validation
def test_distributor_send_reward_epoch_revert_too_short(bob, test_gauge, distributor_contract):
    with ape.reverts("epoch duration must be between 3 days and a year"):
        distributor_contract.send_reward(test_gauge, 10**18, DAY, sender=bob)


def test_distributor_send_reward_epoch_revert_too_long(bob, test_gauge, distributor_contract):
    with ape.reverts("epoch duration must be between 3 days and a year"):
        distributor_contract.send_reward(test_gauge, 10**18, 53 * WEEK, sender=bob)


def test_add_campaign_address(alice, bob, single_campaign, distributor_contract):
    distributor_contract.add_campaign_address(single_campaign, sender=bob)
    assert distributor_contract.campaign_addresses(0) == single_campaign

def test_add_campaign_address_non_contract_revert(alice, bob, distributor_contract):
    with ape.reverts("campaign address must be a contract"):
        distributor_contract.add_campaign_address(bob, sender=bob)


def test_remove_campaign_address(alice, bob, single_campaign, distributor_contract):
    distributor_contract.add_campaign_address(single_campaign, sender=bob)
    assert distributor_contract.campaign_addresses(0) == single_campaign

    distributor_contract.remove_campaign_address(single_campaign, sender=bob)
    assert distributor_contract.get_all_campaign_addresses() == []