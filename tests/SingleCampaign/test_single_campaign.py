import ape
import pytest

DAY = 86400
WEEK = 604800

def test_initial_state(single_campaign, crvusd_token):
    """Test initial state after deployment"""
    assert not single_campaign.is_setup_complete()
    assert not single_campaign.is_reward_epochs_set()
    assert single_campaign.get_number_of_remaining_epochs() == 0
    assert single_campaign.min_epoch_duration() == WEEK
    assert single_campaign.execute_reward_amount() == 10**18
    assert single_campaign.crvusd_address() == crvusd_token.address

def test_guards(bob, charlie, single_campaign):
    assert single_campaign.guards(0) == bob
    assert single_campaign.guards(1) == charlie

def test_set_distributor(bob, distributor, test_gauge, single_campaign):
    # Setup the reward guard and receiver using guard account with default epoch duration (3 days)
    min_epoch_duration = 3 * DAY
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)

    assert single_campaign.distributor_address() == distributor.address
    print(single_campaign.distributor_address())
    assert single_campaign.receiving_gauge() == test_gauge.address
    assert single_campaign.min_epoch_duration() == min_epoch_duration

def test_set_distributor_revert_not_manager(alice, distributor, test_gauge, single_campaign):
    min_epoch_duration = 3 * DAY
    with ape.reverts("only guards can call this function"):
        single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=alice)


def test_set_distributor_revert_already_set(bob, distributor, test_gauge, single_campaign):
    min_epoch_duration = 3 * DAY
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)

    with ape.reverts("Setup already completed"):
        single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)
        
def test_set_reward_epochs(charlie, single_campaign):
    epochs = [1 * 10**18, 2 * 10**18, 3 * 10**18]
    
    # Set new reward epochs using guard account
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    
    assert single_campaign.get_number_of_remaining_epochs() == len(epochs)
    assert single_campaign.is_reward_epochs_set()
    #assert single_campaign.reward_epochs() == epochs

    get_all_epochs = single_campaign.get_all_epochs()
    print(get_all_epochs)

def test_set_reward_only_one_epoch(charlie, single_campaign):
    epochs = [3 * 10**18]
    
    # Set new reward epochs using guard account
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    
    assert single_campaign.get_number_of_remaining_epochs() == len(epochs)
    assert single_campaign.is_reward_epochs_set()

    get_all_epochs = single_campaign.get_all_epochs()
    print(get_all_epochs)


def test_set_reward_epochs_revert_not_guard(alice, single_campaign):
    epochs = [1 * 10**18, 2 * 10**18, 3 * 10**18]
    
    with ape.reverts("only guards can call this function"):
        single_campaign.set_reward_epochs(epochs, sender=alice)

def test_set_reward_epochs_revert_invalid_length(charlie, single_campaign):
    # Try to set 0 epochs
    with ape.reverts("Must set between 1 and 52 epochs"):
        single_campaign.set_reward_epochs([], sender=charlie)
    
    # Try to set more than 52 epochs
    #epochs = [1 * 10**18] * 53
    #with ape.reverts("Must set between 1 and 52 epochs"):
    #    single_campaign.set_reward_epochs(epochs, sender=charlie)

def test_distribution_after_set_epochs(alice, bob, charlie, distributor, single_campaign, reward_token, test_gauge, chain):
    epochs = [1 * 10**18, 2 * 10**18, 3 * 10**18]
    min_epoch_duration = 4 * DAY
    
    # Set new reward epochs
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    
    # Setup the reward guard and receiver addresses with 3 day epoch duration
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=charlie)

    # First distribution - should be 1 tokens
    single_campaign.distribute_reward(sender=bob)

    assert single_campaign.get_number_of_remaining_epochs() == 2
    assert reward_token.balanceOf(test_gauge) == 1 * 10**18

    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()
    
    # Second distribution - should be 2 tokens
    single_campaign.distribute_reward(sender=bob)
    assert single_campaign.get_number_of_remaining_epochs() == 1
    assert reward_token.balanceOf(test_gauge) == 3 * 10**18
    
    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()
    
    # Third distribution - should be 1 token
    single_campaign.distribute_reward(sender=bob)
    assert single_campaign.get_number_of_remaining_epochs() == 0
    assert reward_token.balanceOf(test_gauge) == 6 * 10**18

def test_set_distributor_revert_not_owner(alice, distributor, test_gauge, single_campaign):
    with ape.reverts("only guards can call this function"):
        single_campaign.setup(distributor.address, test_gauge.address, 3 * DAY, 1, "test", sender=alice)

def test_distribution_order(alice, bob, charlie, distributor, single_campaign, reward_token, test_gauge, chain):
    # Setup the reward guard and receiver
    epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    min_epoch_duration = 3 * DAY
    
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=charlie)

    # First distribution - should be 2 tokens
    single_campaign.distribute_reward(sender=bob)

    assert single_campaign.get_number_of_remaining_epochs() == 2
    assert reward_token.balanceOf(test_gauge) == 2 * 10**18

    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()
    
    # Second distribution - should be 1 tokens
    single_campaign.distribute_reward(sender=bob)
    assert single_campaign.get_number_of_remaining_epochs() == 1
    assert reward_token.balanceOf(test_gauge) == 3 * 10**18
    
    # Move time forward one week
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()
    
    # Third distribution - should be 2 tokens
    single_campaign.distribute_reward(sender=bob)
    assert single_campaign.get_number_of_remaining_epochs() == 0
    assert reward_token.balanceOf(test_gauge) == 8 * 10**18


def test_distribution_timing(alice, bob, charlie, distributor, single_campaign, test_gauge, chain):
    epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    min_epoch_duration = 3 * DAY
    DISTRIBUTION_BUFFER = single_campaign.DISTRIBUTION_BUFFER()
    single_campaign.set_reward_epochs(epochs, sender=charlie)

    # Setup the reward guard and receiver
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=charlie)

    # First distribution can happen immediately
    single_campaign.distribute_reward(sender=bob)
    
    # Try to distribute again immediately - should fail
    with ape.reverts("Minimum time between distributions not met"):
        single_campaign.distribute_reward(sender=bob)
    
    # Move time forward less than a min_epoch_duration
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration - DISTRIBUTION_BUFFER - 1000
    chain.mine()
    
    # Should still fail
    with ape.reverts("Minimum time between distributions not met"):
        single_campaign.distribute_reward(sender=bob)
    
    # Move time to exactly one min_epoch_duration
    chain.pending_timestamp = chain.pending_timestamp + 1000
    chain.mine()
    
    # Should succeed now
    single_campaign.distribute_reward(sender=bob)
        
    # Move time forward less than a min_epoch_duration
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration + 10000
    chain.mine()

    # Should succeed now
    single_campaign.distribute_reward(sender=bob)

def test_distribute_revert_no_distributor(bob, single_campaign):
    with ape.reverts("Setup not completed"):
        single_campaign.distribute_reward(sender=bob)

def test_distribute_revert_no_epochs(alice, bob, charlie, distributor, single_campaign, test_gauge, chain):
    epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    min_epoch_duration = 3 * DAY
    single_campaign.set_reward_epochs(epochs, sender=charlie)

    # Setup the reward guard and receiver
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=charlie)

    # Distribute all epochs
    for i in range(3):
        if i > 0:
            chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
            chain.mine()
        single_campaign.distribute_reward(sender=bob)
    
    # Try to distribute when no epochs remain
    with ape.reverts("No remaining reward epochs"):
        single_campaign.distribute_reward(sender=bob)

def test_get_next_epoch_info(alice, bob, charlie, distributor, single_campaign, test_gauge, chain):
    epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    min_epoch_duration = 3 * DAY
    single_campaign.set_reward_epochs(epochs, sender=charlie)

    # Setup the reward guard and receiver
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=charlie)

    # Check initial next epoch
    amount, time_until = single_campaign.get_next_epoch_info()
    assert amount == 2 * 10**18  # First epoch amount
    assert time_until == 0  # No time restriction for first distribution
    
    # Distribute first epoch
    single_campaign.distribute_reward(sender=bob)
    
    # Check second epoch info
    amount, time_until = single_campaign.get_next_epoch_info()
    assert amount == 1 * 10**18  # Second epoch amount
    assert time_until > 0  # Should have time restriction now

    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()

    # Distribute second epoch
    single_campaign.distribute_reward(sender=bob)
    
    # Check third epoch info
    amount, time_until = single_campaign.get_next_epoch_info()
    assert amount == 5 * 10**18  # Third epoch amount
    assert time_until > 0  # Should have time restriction now

def test_get_next_epoch_info_revert_no_epochs(alice, bob, charlie, distributor, single_campaign, test_gauge, chain):
    epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    min_epoch_duration = 3 * DAY

    # Setup the reward guard and receiver
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=charlie)
    
    # Distribute all epochs
    for i in range(3):
        if i > 0:
            chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
            chain.mine()
        single_campaign.distribute_reward(sender=bob)
    
    # Try to get next epoch info when no epochs remain
    with ape.reverts("No remaining reward epochs"):
        single_campaign.get_next_epoch_info()

def test_remaining_epochs_count(alice, bob, charlie, distributor, single_campaign, test_gauge, chain):
    epochs = [2 * 10**18, 1 * 10**18, 5 * 10**18]
    min_epoch_duration = 4 * DAY
    single_campaign.set_reward_epochs(epochs, sender=charlie)

    # Setup the reward guard and receiver
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=charlie)

    # Distribute epochs and check count
    single_campaign.distribute_reward(sender=bob)
    assert single_campaign.get_number_of_remaining_epochs() == 2
    
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()
    single_campaign.distribute_reward(sender=bob)
    assert single_campaign.get_number_of_remaining_epochs() == 1
    
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()
    single_campaign.distribute_reward(sender=bob)
    assert single_campaign.get_number_of_remaining_epochs() == 0

def test_min_epoch_duration_default(single_campaign):
    """Test that min_epoch_duration is initialized to WEEK"""
    assert single_campaign.min_epoch_duration() == WEEK

def test_setup_with_custom_epoch_duration(bob, distributor, test_gauge, single_campaign):
    """Test setting a custom min_epoch_duration during setup"""
    custom_duration = 4 * DAY  # 4 days
    single_campaign.setup(distributor.address, test_gauge.address, custom_duration, 1, "test", sender=bob)
    
    assert single_campaign.min_epoch_duration() == custom_duration
    assert single_campaign.is_setup_complete()

def test_setup_revert_epoch_too_short(bob, distributor, test_gauge, single_campaign):
    """Test that setting too short epoch duration reverts"""
    too_short = 2 * DAY  # 2 days (minimum is 3 days)
    
    with ape.reverts("epoch duration must be between 3 days and a year"):
        single_campaign.setup(distributor.address, test_gauge.address, too_short, 1, "test", sender=bob)

def test_setup_revert_epoch_too_long(bob, distributor, test_gauge, single_campaign):
    """Test that setting too long epoch duration reverts"""
    too_long = 53 * WEEK  # More than a year
    
    with ape.reverts("epoch duration must be between 3 days and a year"):
        single_campaign.setup(distributor.address, test_gauge.address, too_long, 1, "test", sender=bob)

def test_distribution_respects_min_epoch_duration(bob, charlie, distributor, single_campaign, test_gauge, chain):
    """Test that distribution timing respects custom min_epoch_duration"""
    # Setup with 4-day minimum duration
    custom_duration = 4 * DAY
    DISTRIBUTION_BUFFER = single_campaign.DISTRIBUTION_BUFFER()
    epochs = [1 * 10**18, 2 * 10**18]
    
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    single_campaign.setup(distributor.address, test_gauge.address, custom_duration, 1, "test", sender=bob)
    
    # First distribution should work
    single_campaign.distribute_reward(sender=bob)
    
    # Try to distribute before minimum duration - should fail
    chain.pending_timestamp = chain.pending_timestamp + custom_duration - DISTRIBUTION_BUFFER - 1000
    chain.mine()
    
    with ape.reverts("Minimum time between distributions not met"):
        single_campaign.distribute_reward(sender=bob)
    
    # Move past minimum duration - should succeed
    chain.pending_timestamp = chain.pending_timestamp + custom_duration + DISTRIBUTION_BUFFER + 2000  # Move past min duration
    chain.mine()
    
    single_campaign.distribute_reward(sender=bob)

def test_distribution_buffer(chain, bob, charlie, distributor, test_gauge, single_campaign):
    """Test that distribution can occur within the buffer window"""
    # Setup with 1-week minimum duration
    WEEK = single_campaign.WEEK()  # Get constant from contract
    DISTRIBUTION_BUFFER = single_campaign.DISTRIBUTION_BUFFER()

    epochs = [1 * 10**18, 2 * 10**18]
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    single_campaign.setup(distributor.address, test_gauge.address, WEEK, 1, "test", sender=bob)
    
    # First distribution should work
    single_campaign.distribute_reward(sender=bob)
    
    # Try to distribute way too early - should fail
    chain.pending_timestamp = chain.pending_timestamp + WEEK - DISTRIBUTION_BUFFER - 1000  # Just before buffer window
    chain.mine()
    
    with ape.reverts("Minimum time between distributions not met"):
        single_campaign.distribute_reward(sender=bob)
    
    # Move into buffer window - should succeed
    chain.pending_timestamp = chain.pending_timestamp + 1000  # Move into buffer window
    chain.mine()

    # Verify we can get next epoch info
    next_amount, seconds_until_next = single_campaign.get_next_epoch_info()
    assert next_amount == 2 * 10**18
    assert seconds_until_next > 0  # Should have some time until next distribution
        
    single_campaign.distribute_reward(sender=bob)  # Should succeed within buffer window
    

def test_have_rewards_started(bob, charlie, distributor, single_campaign, test_gauge, chain):
    """Test that have_rewards_started is properly set after first distribution"""
    epochs = [1 * 10**18, 2 * 10**18]
    min_epoch_duration = 4 * DAY
    
    # Setup campaign
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)
    
    # Check initial state
    assert not single_campaign.have_rewards_started()
    
    # First distribution
    single_campaign.distribute_reward(sender=bob)
    
    # Verify have_rewards_started is now True
    assert single_campaign.have_rewards_started()
    
    # Verify timing restrictions now apply
    with ape.reverts("Minimum time between distributions not met"):
        single_campaign.distribute_reward(sender=bob)
        
    # Move time forward past minimum epoch duration
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration
    chain.mine()

    # Should now be able to distribute again
    single_campaign.distribute_reward(sender=bob)

def test_execution_allowed(bob, charlie, distributor, single_campaign, test_gauge, chain):
    """Test execution_allowed under various conditions"""
    epochs = [1 * 10**18, 2 * 10**18]
    min_epoch_duration = 4 * DAY
    DISTRIBUTION_BUFFER = single_campaign.DISTRIBUTION_BUFFER()
    
    # Should revert before setup
    with ape.reverts("Setup not completed"):
        single_campaign.execution_allowed()
    
    # Setup campaign
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)
    
    # Should revert before epochs are set
    with ape.reverts("Reward epochs not set"):
        single_campaign.execution_allowed()
    
    # Set reward epochs
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    
    # Should be allowed before first distribution
    assert single_campaign.execution_allowed()
    
    # First distribution
    single_campaign.distribute_reward(sender=bob)
    
    # Should not be allowed immediately after distribution
    assert not single_campaign.execution_allowed()
    
    # Should not be allowed just before buffer window
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration - DISTRIBUTION_BUFFER - 2
    chain.mine()
    assert not single_campaign.execution_allowed()
    
    # Should be allowed within buffer window
    chain.pending_timestamp = chain.pending_timestamp + DISTRIBUTION_BUFFER + 1
    chain.mine()
    assert single_campaign.execution_allowed()
    
    # Distribute all remaining epochs
    single_campaign.distribute_reward(sender=bob)
    
    # Should revert when no epochs remain
    with ape.reverts("No remaining reward epochs"):
        single_campaign.execution_allowed()

def test_execute(bob, charlie, distributor, single_campaign, test_gauge, chain, crvusd_token, reward_token):
    """Test execute function under various conditions"""
    epochs = [1 * 10**18, 2 * 10**18, 3 * 10**18]
    min_epoch_duration = 4 * DAY
    execute_reward = single_campaign.execute_reward_amount()

    # Setup campaign
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    
    # Send crvUSD tokens to contract for execute rewards
    transfer_amount = 4 * 10**18
    crvusd_token.transfer(single_campaign.address, transfer_amount, sender=charlie)
    
    # First epoch
    initial_balance = crvusd_token.balanceOf(charlie)
    single_campaign.execute(sender=charlie)
    assert crvusd_token.balanceOf(charlie) == initial_balance + execute_reward
    
    # Move forward to buffer window
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration - single_campaign.DISTRIBUTION_BUFFER() + 2
    chain.mine()
    
    # Second epoch
    initial_balance = crvusd_token.balanceOf(charlie)
    single_campaign.execute(sender=charlie)
    assert crvusd_token.balanceOf(charlie) == initial_balance + execute_reward
    
    # Move forward for third epoch
    chain.pending_timestamp = chain.pending_timestamp + min_epoch_duration - single_campaign.DISTRIBUTION_BUFFER() + 2
    chain.mine()
    
    # Third epoch
    initial_balance = crvusd_token.balanceOf(charlie)
    single_campaign.execute(sender=charlie)
    assert crvusd_token.balanceOf(charlie) == initial_balance + execute_reward

def test_execute_without_crvusd(bob, charlie, distributor, single_campaign, test_gauge, chain, crvusd_token):
    """Test execute function fails when contract has no crvUSD"""
    epochs = [1 * 10**18, 2 * 10**18]
    min_epoch_duration = 4 * DAY
    
    # Setup campaign
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)
    single_campaign.set_reward_epochs(epochs, sender=charlie)

    # should work even if no crvUSD present
    assert single_campaign.execute(sender=charlie)

def test_execute_with_crvusd(bob, charlie, distributor, single_campaign, test_gauge, chain, crvusd_token):
    """Test execute function works when contract has crvUSD"""
    epochs = [1 * 10**18, 2 * 10**18]
    min_epoch_duration = 4 * DAY
    execute_reward = single_campaign.execute_reward_amount()
    
    # Send crvUSD tokens to contract for execute rewards
    crvusd_token.transfer(single_campaign, 4 * 10**18, sender=charlie)
    
    # Setup and test execution
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    
    initial_balance = crvusd_token.balanceOf(charlie)
    single_campaign.execute(sender=charlie)
    assert crvusd_token.balanceOf(charlie) == initial_balance + execute_reward
    

def test_deploy_single_proxy(bob, single_campaign, proxy):
    """Test deploying a single proxy"""
    implementation = single_campaign.address
    
    # Deploy proxy
    proxy_address = proxy.deploy_proxy(implementation, sender=bob)
    
    # Verify proxy was created
    assert proxy_address != implementation

def test_deploy_multiple_proxies(bob, single_campaign, proxy):
    """Test deploying multiple proxies"""
    implementation = single_campaign.address
    num_proxies = 10
    
    # Deploy proxies
    tx = proxy.deploy_multiple_proxies(implementation, num_proxies, sender=bob)
    proxy_addresses = tx.return_value
    
    # Verify correct number of proxies created
    assert len(proxy_addresses) == num_proxies
    
    # Verify each proxy was created properly
    for proxy_address in proxy_addresses:
        assert proxy_address != implementation
    
def test_deploy_multiple_proxies_max_limit(bob, single_campaign, proxy):
    """Test deploying maximum number of proxies (27)"""
    implementation = single_campaign.address
    num_proxies = 27
    
    # Deploy maximum number of proxies
    tx = proxy.deploy_multiple_proxies(implementation, num_proxies, sender=bob)
    proxy_addresses = tx.return_value
    
    print(tx)
    print(proxy_addresses)
    # Verify correct number of proxies created
    assert len(proxy_addresses) == num_proxies

def test_deploy_multiple_proxies_revert_over_limit(bob, single_campaign, proxy):
    """Test deploying more than maximum allowed proxies reverts"""
    implementation = single_campaign.address
    num_proxies = 28  # Over the 27 limit
    
    # Attempt to deploy too many proxies
    with ape.reverts():  # Should revert due to exceeding max bound
        proxy.deploy_multiple_proxies(implementation, num_proxies, sender=bob)

def test_recover_crvusd_token(bob, charlie, diana, crvusd_token, single_campaign):
    amount = 10 ** 18
    crvusd_token.transfer(single_campaign, amount, sender=charlie)
    assert crvusd_token.balanceOf(single_campaign) == amount
    # rest of lost token on charlies address, start with 10 ** 19
    assert crvusd_token.balanceOf(charlie) == 9 * amount
    # recover lost token to diana (recovery address)
    single_campaign.recover_token(crvusd_token, bob, amount, sender=bob)
    assert crvusd_token.balanceOf(bob) == amount

def test_recover_token_revert_guard(alice, charlie, crvusd_token, single_campaign):
    with ape.reverts("only reward guards can call this function"):
        single_campaign.recover_token(crvusd_token, charlie, 10 ** 18, sender=alice)

def test_recover_token_revert_amount(bob, charlie, crvusd_token, single_campaign):
    with ape.reverts("amount must be greater than 0"):
        single_campaign.recover_token(crvusd_token, charlie, 0,  sender=bob)

def test_recover_token_revert_target_address(alice, bob, crvusd_token, single_campaign):
    with ape.reverts("only guards allowed to receive token"):
        single_campaign.recover_token(crvusd_token, alice, 10 ** 18, sender=bob)

def test_next_execution_times(bob, charlie, distributor, single_campaign, test_gauge, chain):
    """Test next execution time functions"""
    epochs = [1 * 10**18, 2 * 10**18]
    min_epoch_duration = 4 * DAY
    DISTRIBUTION_BUFFER = single_campaign.DISTRIBUTION_BUFFER()
    
    # Setup campaign
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    
    # Before first distribution
    assert single_campaign.next_execution_allowed_time() ==  min_epoch_duration
    assert single_campaign.next_execution_allowed_time_buffer() == min_epoch_duration - DISTRIBUTION_BUFFER
    
    # First distribution
    single_campaign.distribute_reward(sender=bob)
    distribution_time = chain.pending_timestamp
    
    # After first distribution
    expected_next_time = distribution_time + min_epoch_duration
    expected_next_time_buffer = expected_next_time - DISTRIBUTION_BUFFER
    
    assert single_campaign.next_execution_allowed_time() == expected_next_time -1 
    assert single_campaign.next_execution_allowed_time_buffer() == expected_next_time_buffer -1 

def test_next_execution_payment_amount(bob, charlie, distributor, single_campaign, test_gauge, crvusd_token):
    """Test next execution payment amount function"""
    epochs = [1 * 10**18]
    min_epoch_duration = 4 * DAY
    execute_reward = single_campaign.execute_reward_amount()
    
    # Setup campaign
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    
    # Without any crvUSD in contract
    assert single_campaign.next_execution_payment_amount() == 0
    
    # Send some crvUSD to contract
    crvusd_token.transfer(single_campaign.address, execute_reward, sender=charlie)
    assert single_campaign.next_execution_payment_amount() == execute_reward
    
    # Send more than needed
    crvusd_token.transfer(single_campaign.address, execute_reward, sender=charlie)
    assert single_campaign.next_execution_payment_amount() == execute_reward

def test_remove_reward_epochs(bob, charlie, distributor, single_campaign, test_gauge):
    """Test removing reward epochs"""
    epochs = [1 * 10**18, 2 * 10**18, 3 * 10**18]
    min_epoch_duration = 4 * DAY
    
    # Setup campaign
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    
    # Verify initial state
    assert single_campaign.get_number_of_remaining_epochs() == 3
    assert single_campaign.is_reward_epochs_set()
    
    # Remove epochs
    single_campaign.remove_reward_epochs(sender=bob)
    
    # Verify epochs were removed
    assert single_campaign.get_number_of_remaining_epochs() == 0
    # Flag should still be true to prevent reuse
    assert single_campaign.is_reward_epochs_set()

    with ape.reverts("No remaining reward epochs"):
        single_campaign.execution_allowed()


def test_remove_reward_epochs_revert_not_guard(alice, bob, charlie, distributor, single_campaign, test_gauge):
    """Test that non-guards cannot remove reward epochs"""
    epochs = [1 * 10**18, 2 * 10**18]
    min_epoch_duration = 4 * DAY
    
    # Setup campaign
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    
    # Try to remove epochs with non-guard account
    with ape.reverts("only guards can call this function"):
        single_campaign.remove_reward_epochs(sender=alice)

def test_remove_reward_epochs_revert_not_set(bob, distributor, single_campaign, test_gauge):
    """Test that epochs cannot be removed if not set"""
    min_epoch_duration = 4 * DAY
    
    # Setup campaign but don't set epochs
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)
    
    # Try to remove unset epochs
    with ape.reverts("only can be used on set epochs"):
        single_campaign.remove_reward_epochs(sender=bob)

def test_remove_reward_epochs_prevents_distribution(bob, charlie, distributor, single_campaign, test_gauge):
    """Test that distributions cannot happen after epochs are removed"""
    epochs = [1 * 10**18, 2 * 10**18]
    min_epoch_duration = 4 * DAY
    
    # Setup campaign
    single_campaign.setup(distributor.address, test_gauge.address, min_epoch_duration, 1, "test", sender=bob)
    single_campaign.set_reward_epochs(epochs, sender=charlie)
    
    # Remove epochs
    single_campaign.remove_reward_epochs(sender=bob)
    
    # Try to distribute rewards
    with ape.reverts("No remaining reward epochs"):
        single_campaign.distribute_reward(sender=bob)