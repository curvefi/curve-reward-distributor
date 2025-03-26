#pragma version ^0.4.0
"""
@title SingleCampaign for L2
@author curve.fi
@license MIT
@notice Distributes variable rewards for one gauge through Distributor
@custom:version 0.0.3
@custom:security security@curve.fi
"""

VERSION: public(constant(String[8])) = "0.0.3"

from ethereum.ercs import IERC20

interface IDistributor:
    def send_reward_token(_receiving_gauge: address, _amount: uint256, _epoch: uint256): nonpayable
    def reward_token() -> address: view
    def remove_active_campaign_address(_campaign_address: address): nonpayable

# State Variables
guards: public(DynArray[address, 5])  # Changed from owner to guards
distributor_address: public(address)
receiving_gauge: public(address)
min_epoch_duration: public(uint256)
id: public(uint256)
name: public(String[64])

is_setup_complete: public(bool)
is_reward_epochs_set: public(bool)

reward_epochs: public(DynArray[uint256, 52])  # Storing reward amounts
last_reward_distribution_time: public(uint256)
have_rewards_started: public(bool)
last_reward_amount: public(uint256)

execute_reward_amount: public(uint256)
crvusd_address: public(address)

WEEK: public(constant(uint256)) = 7 * 24 * 60 * 60  # 1 week in seconds
DISTRIBUTION_BUFFER: public(constant(uint256)) = 2 * 60 * 60  # 2 hour window for early distribution, max divation is 2.7%

# Events

event SetupCompleted:
    distributor_address: address
    receiving_gauge: address
    min_epoch_duration: uint256
    timestamp: uint256

event RewardEpochsSet:
    reward_epochs: DynArray[uint256, 52]
    timestamp: uint256

event EndCampaign:
    timestamp: uint256

event RemoveActiveCampaignAddress:
    distributor_address: address
    campaign_address: address
    timestamp: uint256

event RewardDistributed:
    reward_amount: uint256
    epoch_duration: uint256
    end_time: uint256
    end_time_buffer: uint256
    remaining_reward_epochs: uint256
    timestamp: uint256

event ExecuteRewardDistributed:
    caller: address
    epoch_number: uint256
    reward_amount: uint256
    reward_token: address
    execute_reward_amount: uint256
    timestamp: uint256


@deploy
def __init__(_guards: DynArray[address, 5], _crvusd_address: address, _execute_reward_amount: uint256):
    """
    @notice Initialize the contract with guards
    @param _guards List of guard addresses that can control the contract
    @param _crvusd_address Address of the crvUSD token to be distributed to the caller
    @param _execute_reward_amount Amount of crvUSD to be distributed to the caller
    @dev min_epoch_duration reflects the old default in legacy gauge contracts
    """
    self.guards = _guards
    self.min_epoch_duration = WEEK
    self.crvusd_address = _crvusd_address
    self.execute_reward_amount = _execute_reward_amount

@external
def setup(_distributor_address: address, _receiving_gauge: address, _min_epoch_duration: uint256, _id: uint256, _name: String[64]):
    """
    @notice Set the reward guard and receiver addresses (can only be set once)
    @param _distributor_address Address of the Distributor contract
    @param _receiving_gauge Address of the RewardReceiver contract
    @param _min_epoch_duration Minimum epoch duration in seconds
    """
    assert msg.sender in self.guards, "only guards can call this function"
    assert not self.is_setup_complete, "Setup already completed"
    assert 3 * WEEK // 7 <= _min_epoch_duration and _min_epoch_duration <= WEEK  * 4 * 12, 'epoch duration must be between 3 days and a year'

    self.distributor_address = _distributor_address
    self.receiving_gauge = _receiving_gauge
    self.min_epoch_duration = _min_epoch_duration
    self.id = _id
    self.name = _name

    self.is_setup_complete = True

    log SetupCompleted(_distributor_address, _receiving_gauge, _min_epoch_duration, block.timestamp)


@external
def set_reward_epochs(_reward_epochs: DynArray[uint256, 52]):
    """
    @notice  Set the reward epochs in reverse order: last value is the first to be distributed, first value is the last to be distributed
    @param _reward_epochs List of reward amounts ordered from first to last epoch
    @dev Be aware that internal storage is reversed, to use pop() to get the next epoch from last entry first
    """
    assert msg.sender in self.guards, "only guards can call this function"
    assert not self.is_reward_epochs_set, "Reward epochs can only be set once"
    assert len(_reward_epochs) > 0 and len(_reward_epochs) <= 52, "Must set between 1 and 52 epochs"

    # Store epochs in reverse order
    n: uint256 = len(_reward_epochs)

    for i: uint256 in range(n, bound=52):
        self.reward_epochs.append(_reward_epochs[n - 1 - i])

    self.is_reward_epochs_set = True

    log RewardEpochsSet(_reward_epochs, block.timestamp)


@external
def distribute_reward():
    self._distribute_reward()

@internal
def _distribute_reward():
    """
    @notice Distribute rewards for the current epoch if conditions are met
    """
    assert self.is_setup_complete, "Setup not completed"
    assert self.is_reward_epochs_set, "Reward epochs not set"
    assert len(self.reward_epochs) > 0, "No remaining reward epochs"

    end_time: uint256 = 0
    end_time_buffer: uint256 = 0

    # For subsequent distributions, check if minimum time has passed
    # @dev the DISTRIBUTION_BUFFER allows to distribute the reward earlier than the min_epoch_duration, to allow continuous distribution
    if self.have_rewards_started:
        end_time = self.last_reward_distribution_time + self.min_epoch_duration
        end_time_buffer = end_time - DISTRIBUTION_BUFFER
        assert block.timestamp >= end_time_buffer, "Minimum time between distributions not met"

    # get the last value of the reward epochs array, internaly this is the next amount to be distributed
    reward_amount: uint256 = self.reward_epochs.pop()

    # Check if distributor has enough balance to send reward
    reward_token: address = staticcall IDistributor(self.distributor_address).reward_token()
    assert staticcall IERC20(reward_token).balanceOf(self.distributor_address) >= reward_amount, "Distributor has no reward token to distribute"


    # Update last distribution time and mark rewards as started
    self.last_reward_distribution_time = block.timestamp

    # Calculate end_time for logging purposes only for subsequent distributions
    if (not self.have_rewards_started):
        end_time = self.last_reward_distribution_time + self.min_epoch_duration
        end_time_buffer = end_time - DISTRIBUTION_BUFFER

    self.have_rewards_started = True

    # Call reward guard to send reward
    extcall IDistributor(self.distributor_address).send_reward_token(self.receiving_gauge, reward_amount, self.min_epoch_duration)

    self.last_reward_amount = reward_amount


    log RewardDistributed(
        reward_amount,
        self.min_epoch_duration,
        end_time,
        end_time_buffer,
        len(self.reward_epochs),  # Remaining reward epochs
        block.timestamp
    )

@external
def execute():
    """
    @notice Execute the reward distribution
    @dev no timestamp update needed as timestamp is updated in distribute_reward()
    """
    # Check if execution is allowed
    assert  self._execution_allowed(), "Too early"

    # Do the actual work here
    self._distribute_reward()

    # Check if contract has enough crvUSD balance to pay reward
    # Pay crvUSD reward to caller
    if staticcall IERC20(self.crvusd_address).balanceOf(self) >= self.execute_reward_amount:
        assert extcall IERC20(self.crvusd_address).transfer(msg.sender, self.execute_reward_amount, default_return_value=True)

    log ExecuteRewardDistributed(
        msg.sender,
        len(self.reward_epochs),
        self.last_reward_amount,
        self.crvusd_address,
        self.execute_reward_amount,
        block.timestamp
    )

@external
def end_campaign():
    """
    @notice  remove the reward epochs
    @dev a way to end the campaign early
    """
    assert msg.sender in self.guards, "only guards can call this function"
    assert self.is_reward_epochs_set, "only can be used on set epochs"
    assert len(self.reward_epochs) > 0, "No remaining reward epochs"

    # Store epochs lenght
    n: uint256 = len(self.reward_epochs)

    for i: uint256 in range(n, bound=52):
        self.reward_epochs.pop()
    # For now we don't want to reset the reward epochs set flag, so campaign can't be reused
    # self.is_reward_epochs_set = False

    self._remove_active_campaign_address()

    log EndCampaign(block.timestamp)

@external
def remove_active_campaign_address():
    """
    @notice Remove an active campaign address from the distributor
    """
    assert msg.sender in self.guards, "only guards can call this function"
    assert self.is_reward_epochs_set, "only can be used on set epochs"

    self._remove_active_campaign_address()

@internal
def _remove_active_campaign_address():
    """
    @notice Remove an active campaign address from the distributor
    """
    assert msg.sender in self.guards, "only guards can call this function"
    assert self.is_reward_epochs_set, "only can be used on set epochs"

    extcall IDistributor(self.distributor_address).remove_active_campaign_address(self)

    log RemoveActiveCampaignAddress(
        self.distributor_address,
        self,
        block.timestamp
    )


@external
@view
def execution_allowed() -> bool:
    return self._execution_allowed()


@internal
@view
def _execution_allowed() -> bool:
    """
    @notice Check if execution is allowed
    @return bool True if execution is allowed, False otherwise
    """
    assert self.is_setup_complete, "Setup not completed"
    assert self.is_reward_epochs_set, "Reward epochs not set"
    assert len(self.reward_epochs) > 0, "No remaining reward epochs"

    # get the last position of the reward epochs array, internaly this is the next amount to be distributed
    reward_amount: uint256 = self.reward_epochs[len(self.reward_epochs)-1]

    # Check if distributor has enough balance to send reward
    reward_token: address = staticcall IDistributor(self.distributor_address).reward_token()

    if staticcall IERC20(reward_token).balanceOf(self.distributor_address) < reward_amount:
        return False

    # start execution is always possible if not started
    if not self.have_rewards_started:
        return True

    # check if minimum time has passed since last distribution
    if block.timestamp >= self.last_reward_distribution_time + self.min_epoch_duration - DISTRIBUTION_BUFFER:
        return True
    else:
        return False

@external
@view
def next_execution_allowed_time() -> uint256:
    """
    @notice Get the time when execution is allowed
    @return uint256 timestamp when execution is allowed
    """
    return self.last_reward_distribution_time + self.min_epoch_duration

@external
@view
def next_execution_allowed_time_buffer() -> uint256:
    """
    @notice Get the time when execution is allowed
    @return uint256 timestamp when earliest execution is allowed
    """
    return self.last_reward_distribution_time + self.min_epoch_duration - DISTRIBUTION_BUFFER

@external
@view
def next_execution_payment_amount() -> uint256:
    """
    @notice Get the amount of crvUSD that will be paid to the caller when execution is allowed
    @return uint256 amount of crvUSD that will be paid to the caller
    """
    if staticcall IERC20(self.crvusd_address).balanceOf(self) >= self.execute_reward_amount:
        return self.execute_reward_amount
    else:
        return 0


@external
@view
def get_next_epoch_info() -> (uint256, uint256):
    """
    @notice Get information about the next epoch to be distributed
    @return tuple(
        next_reward_amount: Amount for next epoch,
        seconds_until_next_distribution: Seconds left until next distribution is allowed
    )
    """
    assert len(self.reward_epochs) > 0, "No remaining reward epochs"

    seconds_until_next_distribution: uint256 = 0
    if self.have_rewards_started:
        if block.timestamp < self.last_reward_distribution_time + self.min_epoch_duration:
            seconds_until_next_distribution = self.last_reward_distribution_time + self.min_epoch_duration - block.timestamp

    return (
        self.reward_epochs[len(self.reward_epochs) - 1],  # Next reward amount to distribute (last element)
        seconds_until_next_distribution
    )


@external
@view
def get_all_epochs() -> DynArray[uint256, 52]:
    """
    @notice Get all remaining reward epochs
    @return DynArray[uint256, 52] Array containing all remaining reward epoch amounts
    @dev returns the epochs list as the same order as they are set in set_reward_epochs()
    @dev Be aware that internal storage is reversed, to use pop() to get the next epoch
    """
    reward_epochs: DynArray[uint256, 52] = []

    n: uint256 = len(self.reward_epochs)
    for i: uint256 in range(n, bound=52):
        reward_epochs.append(self.reward_epochs[n - 1 - i])

    return reward_epochs


@external
def recover_token(_token: address, target_address: address, _amount: uint256):
    """
    @notice recover wrong token from contract to recovery address
    @param _token address of the token to recover
    @param target_address address of the target to receive the token
    @param _amount amount of the token to recover
    """
    assert msg.sender in self.guards, 'only reward guards can call this function'
    assert target_address in self.guards, 'only guards allowed to receive token'

    assert _amount > 0, 'amount must be greater than 0'

    assert extcall IERC20(_token).transfer(target_address, _amount, default_return_value=True)


@external
@view
def get_all_guards() -> DynArray[address, 5]:
    """
    @notice Get all guards
    @return DynArray[address, 3] Array containing all guards
    """
    return self.guards

@external
@view
def get_number_of_remaining_epochs() -> uint256:
    """
    @notice Get the number of remaining reward epochs
    @return uint256 Remaining number of reward epochs
    """
    return len(self.reward_epochs)
