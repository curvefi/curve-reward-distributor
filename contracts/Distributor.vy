#pragma version ^0.4.0
"""
@title Distributor
@author curve.fi
@license MIT
@notice Distributes variable rewards for one gauge through Distributor
@custom:version 0.0.4
@custom:security security@curve.fi
"""

VERSION: public(constant(String[8])) = "0.0.4"

from ethereum.ercs import IERC20

interface LegacyGauge:
    def deposit_reward_token(_reward_token: address, _amount: uint256): nonpayable

interface Gauge:
    def deposit_reward_token(_reward_token: address, _amount: uint256, _epoch: uint256): nonpayable

interface PassThrough:
    def deposit_reward_token(_reward_token: address, _amount: uint256, _epoch: uint256): nonpayable
    def deposit_reward(_amount: uint256, _epoch: uint256): nonpayable
    def deposit_reward_token_with_receiver(_reward_receiver: address, _reward_token: address, _amount: uint256, _epoch: uint256): nonpayable

WEEK: constant(uint256) = 7 * 24 * 60 * 60  # 1 week in seconds

guards: public(DynArray[address, 40])
reward_token: public(address)
receiving_gauges: public(DynArray[address, 20])
recovery_address: public(address)
active_campaign_addresses: public(DynArray[address, 30])

event SentRewardToken:
    receiving_gauge: address
    reward_token: address
    amount: uint256
    epoch: uint256
    timestamp: uint256

event SentReward:
    receiving_gauge: address
    reward_token: address
    amount: uint256
    epoch: uint256
    timestamp: uint256

event AddActiveCampaignAddress:
    campaign_address: address
    timestamp: uint256

event RemoveCampaignAddress:
    campaign_address: address
    timestamp: uint256

event RecoverToken:
    token: address
    amount: uint256
    timestamp: uint256

@deploy
def __init__(_guards: DynArray[address, 40], _reward_token: address, _receiving_gauges: DynArray[address, 20], _recovery_address: address):
    """
    @notice Contract constructor
    @param _guards set guards who can send reward token to gauges
    @param _reward_token set reward token address
    @param _receiving_gauges allowed gauges to receiver reward
    @param _recovery_address set recovery address
    """
    self.guards = _guards
    self.reward_token = _reward_token
    self.receiving_gauges = _receiving_gauges
    self.recovery_address = _recovery_address

@external
def send_reward_token(_receiving_gauge: address, _amount: uint256, _epoch: uint256 = WEEK):
    """
    @notice send reward token from contract to gauge
    @param _receiving_gauge gauges to receiver reward
    @param _amount The amount of reward token being sent
    @param _epoch The duration the rewards are distributed across in seconds. Between 3 days and a year, week by default
    """
    assert msg.sender in self.guards, 'only reward guards can call this function'
    assert _receiving_gauge in self.receiving_gauges, 'only reward receiver which are allowed'
    assert 3 * WEEK // 7 <= _epoch and _epoch <= WEEK * 4 * 12, 'epoch duration must be between 3 days and a year'
    assert extcall IERC20(self.reward_token).approve(_receiving_gauge, _amount, default_return_value=True)

    self._add_active_campaign_address(msg.sender)

    # legacy gauges have no epoch parameter
    # new deposit_reward_token has epoch parameter default to WEEK
    if _epoch == WEEK:
       extcall LegacyGauge(_receiving_gauge).deposit_reward_token(self.reward_token, _amount)
    else:
       extcall Gauge(_receiving_gauge).deposit_reward_token(self.reward_token, _amount, _epoch)

    log SentRewardToken(_receiving_gauge, self.reward_token, _amount, _epoch, block.timestamp)

@external
def send_reward(_receiving_gauge: address, _amount: uint256, _epoch: uint256 = WEEK):
    """
    @notice send reward token from contract to gauge
    @param _receiving_gauge gauges to receiver reward
    @param _amount The amount of reward token being sent
    @param _epoch The duration the rewards are distributed across in seconds. Between 3 days and a year, week by default
    @dev Todo: not working yet, add passthrough config somewhere
    """
    assert msg.sender in self.guards, 'only reward guards can call this function'
    assert _receiving_gauge in self.receiving_gauges, 'only reward receiver which are allowed'
    assert 3 * WEEK // 7 <= _epoch and _epoch <= WEEK * 4 * 12, 'epoch duration must be between 3 days and a year'
    assert extcall IERC20(self.reward_token).approve(_receiving_gauge, _amount, default_return_value=True)

    passthrough: address = _receiving_gauge

    self._add_active_campaign_address(msg.sender)

    extcall PassThrough(passthrough).deposit_reward_token_with_receiver(_receiving_gauge, self.reward_token, _amount, _epoch)

    log SentReward(_receiving_gauge, self.reward_token, _amount, _epoch, block.timestamp)

@internal
def _add_active_campaign_address(_campaign_address: address):
    if _campaign_address not in self.active_campaign_addresses:
        self.active_campaign_addresses.append(_campaign_address)
        log AddActiveCampaignAddress(_campaign_address, block.timestamp)

@external
def remove_active_campaign_address(_campaign_address: address):
    """
    @notice Remove an active campaign address from the list
    @param _campaign_address The address of the campaign to remove
    """
    assert msg.sender in self.guards, 'only reward guards can call this function'

    for i: uint256 in range(len(self.active_campaign_addresses), bound=30):
        if self.active_campaign_addresses[i] == _campaign_address:
            last_idx: uint256 = len(self.active_campaign_addresses) - 1
            if i != last_idx:
                self.active_campaign_addresses[i] = self.active_campaign_addresses[last_idx]
            self.active_campaign_addresses.pop()
            log RemoveCampaignAddress(_campaign_address, block.timestamp)
            break

    assert _campaign_address not in self.active_campaign_addresses, "campaign address was not successfully removed"

@external
def recover_token(_token: address, _amount: uint256):
    """
    @notice recover wrong token from contract to recovery address
    @param _amount amount of the token to recover
    """
    assert msg.sender in self.guards, 'only reward guards can call this function'
    assert _amount > 0, 'amount must be greater than 0'

    assert extcall IERC20(_token).transfer(self.recovery_address, _amount, default_return_value=True)

    log RecoverToken(_token, _amount, block.timestamp)

@external
@view
def get_all_guards() -> DynArray[address, 40]:
    """
    @notice Get all guards
    @return DynArray[address, 40] list containing all guards
    """
    return self.guards

@external
@view
def get_all_receiving_gauges() -> DynArray[address, 20]:
    """
    @notice Get all reward receivers
    @return DynArray[address, 20] list containing all reward receivers
    """
    return self.receiving_gauges

@external
@view
def get_all_active_campaign_addresses() -> DynArray[address, 30]:
    """
    @notice Get all active campaign addresses
    @return DynArray[address, 30] list containing all active campaign addresses
    """
    return self.active_campaign_addresses
