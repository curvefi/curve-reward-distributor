import ape

DAY = 86400
WEEK = 604800


def test_distributor_guards(bob, charlie, distributor):
    assert distributor.guards(0) == bob
    assert distributor.guards(1) == charlie


def test_distributor_reward_token(bob, reward_token, distributor):
    assert distributor.reward_token() == reward_token


def test_distributor_receivers(bob, test_gauge, distributor):
    receiving_gauges = distributor.receiving_gauges(0)
    print(receiving_gauges)
    assert test_gauge == receiving_gauges


# send reward token to reward guard contract, then deposit_reward_tokens
def test_distributor_send_reward_token(alice, bob, diana, reward_token, test_gauge, distributor):
    amount = 10**16
    distributor_balance = reward_token.balanceOf(distributor, sender=alice)
    assert distributor_balance == 0
    reward_token.transferFrom(bob, distributor, amount, sender=bob)
    distributor_balance = reward_token.balanceOf(distributor, sender=alice)
    assert distributor_balance == amount
    distributor.send_reward_token(test_gauge, amount, sender=bob)
    assert test_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(diana, sender=alice)
    assert amount == balance_recoverd
    assert amount == distributor_balance


def test_distributor_send_reward_token_epoch(
    alice, bob, diana, reward_token, test_gauge, distributor
):
    amount = 10**16
    distributor_balance = reward_token.balanceOf(distributor, sender=alice)
    assert distributor_balance == 0
    reward_token.transferFrom(bob, distributor, amount, sender=bob)
    distributor_balance = reward_token.balanceOf(distributor, sender=alice)
    assert distributor_balance == amount
    distributor.send_reward_token(test_gauge, amount, 8 * DAY, sender=bob)
    assert test_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(diana, sender=alice)
    assert amount == balance_recoverd
    assert amount == distributor_balance


def test_distributor_send_reward_token_active_campaign_addresses(
    alice, bob, diana, reward_token, test_gauge, distributor
):
    amount = 10**16
    distributor_balance = reward_token.balanceOf(distributor, sender=alice)
    assert distributor_balance == 0
    reward_token.transferFrom(bob, distributor, amount, sender=bob)
    distributor_balance = reward_token.balanceOf(distributor, sender=alice)
    assert distributor_balance == amount
    distributor.send_reward_token(test_gauge, amount, 8 * DAY, sender=bob)

    assert distributor.active_campaign_addresses(0) == bob
    active_addresses = distributor.get_all_active_campaign_addresses()
    assert active_addresses[0] == bob


def test_distributor_sent_revert(alice, test_gauge, distributor):
    with ape.reverts("only reward guards can call this function"):
        distributor.send_reward_token(test_gauge, 10**18, sender=alice)


def test_distributor_epoch_revert_too_short(bob, test_gauge, distributor):
    with ape.reverts("epoch duration must be between 3 days and a year"):
        distributor.send_reward_token(test_gauge, 10**18, DAY, sender=bob)


def test_distributor_epoch_revert_too_long(bob, test_gauge, distributor):
    with ape.reverts("epoch duration must be between 3 days and a year"):
        distributor.send_reward_token(test_gauge, 10**18, 53 * WEEK, sender=bob)


def test_recover_token(bob, charlie, diana, lost_token, distributor):
    amount = 10**18
    lost_token.transferFrom(charlie, distributor, amount, sender=charlie)
    assert lost_token.balanceOf(distributor) == amount
    # rest of lost token on charlies address, start with 10 ** 19
    assert lost_token.balanceOf(charlie) == 9 * amount
    # recover lost token to diana (recovery address)
    distributor.recover_token(lost_token, amount, sender=bob)
    assert lost_token.balanceOf(diana) == amount


def test_recover_reward_token(bob, charlie, diana, reward_token, distributor):
    amount = 10**18
    reward_token.transferFrom(bob, distributor, amount, sender=bob)
    assert reward_token.balanceOf(distributor) == amount
    # rest of lost token on charlies address, start with 10 ** 19
    assert reward_token.balanceOf(bob) == 9 * amount
    # recover lost token to diana (recovery address)
    distributor.recover_token(reward_token, amount, sender=bob)
    assert reward_token.balanceOf(diana) == amount


def test_recover_token_revert_manager(alice, lost_token, distributor):
    with ape.reverts("only reward guards can call this function"):
        distributor.recover_token(lost_token, 10**18, sender=alice)


def test_recover_token_revert_amount(bob, lost_token, distributor):
    with ape.reverts("amount must be greater than 0"):
        distributor.recover_token(lost_token, 0, sender=bob)


def test_remove_active_campaign_address(alice, bob, charlie, reward_token, test_gauge, distributor):
    """Test removing active campaign addresses"""
    # First send a reward to add a campaign address
    amount = 10**16
    reward_token.transferFrom(bob, distributor, amount, sender=bob)

    distributor.send_reward_token(test_gauge, amount, sender=bob)

    # Verify active campaign address is in the list
    assert distributor.active_campaign_addresses(0) == bob
    active_addresses = distributor.get_all_active_campaign_addresses()
    print(active_addresses)
    assert active_addresses[0] == bob

    # Remove active campaign address
    distributor.remove_active_campaign_address(bob, sender=bob)

    # Verify active campaign address was removed
    active_addresses = distributor.get_all_active_campaign_addresses()
    print(active_addresses)
    assert len(active_addresses) == 0


def test_remove_active_campaign_address_revert_non_guard(
    alice, bob, reward_token, test_gauge, distributor
):
    """Test that non-guards cannot remove active campaign addresses"""
    # First send a reward to add a campaign address
    amount = 10**16
    reward_token.transferFrom(bob, distributor, amount, sender=bob)
    distributor.send_reward_token(test_gauge, amount, sender=bob)

    with ape.reverts("only reward guards can call this function"):
        distributor.remove_active_campaign_address(bob, sender=alice)
