#pragma version ^0.4.0
"""
@title Distributor
@author martinkrung for curve.fi
@license MIT
@notice reward guard contract who can deposit a fixed reward token to allowed gauges
"""

from ethereum.ercs import IERC20

interface LegacyGauge:
    def deposit_reward_token(_reward_token: address, _amount: uint256): nonpayable

interface Gauge:
    def deposit_reward_token(_reward_token: address, _amount: uint256, _epoch: uint256): nonpayable

WEEK: constant(uint256) = 7 * 24 * 60 * 60  # 1 week in seconds
VERSION: constant(String[8]) = "0.9.1"

guards: public(DynArray[address, 30])
reward_token: public(address)
receiving_gauges: public(DynArray[address, 20])
recovery_address: public(address)
campaign_addresses: public(DynArray[address, 30])

event SentRewardToken:
    receiving_gauge: address
    reward_token: address
    amount: uint256
    _epoch: uint256
    timestamp: uint256


@deploy
def __init__(_guards: DynArray[address, 30], _reward_token: address, _receiving_gauges: DynArray[address, 20], _recovery_address: address):
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

    self.campaign_addresses.append(msg.sender)

    # legacy gauges have no epoch parameter 
    # new deposit_reward_token has epoch parameter default to WEEK
    if _epoch == WEEK:
       extcall LegacyGauge(_receiving_gauge).deposit_reward_token(self.reward_token, _amount)
    else:
       extcall Gauge(_receiving_gauge).deposit_reward_token(self.reward_token, _amount, _epoch)

    log SentRewardToken(_receiving_gauge, self.reward_token, _amount, _epoch, block.timestamp)


@external
def remove_campaign_address(_campaign_address: address):
    """
    @notice Remove a campaign address from the list
    @param _campaign_address The address of the campaign to remove
    """
    assert msg.sender in self.guards, 'only reward guards can call this function'
    
    for i: uint256 in range(len(self.campaign_addresses), bound=30):
         # Move the last element to the found i and pop the last element
        if self.campaign_addresses[i] == _campaign_address:    
            last_idx: uint256 = len(self.campaign_addresses) - 1
            if i != last_idx:
                self.campaign_addresses[i] = self.campaign_addresses[last_idx]
            self.campaign_addresses.pop()

@external
def recover_token(_token: address, _amount: uint256):
    """
    @notice recover wrong token from contract to recovery address
    @param _amount amount of the token to recover
    """
    assert msg.sender in self.guards, 'only reward guards can call this function'
    assert _amount > 0, 'amount must be greater than 0'

    assert extcall IERC20(_token).transfer(self.recovery_address, _amount, default_return_value=True)

@external
@view
def get_all_guards() -> DynArray[address, 30]:
    """
    @notice Get all guards
    @return DynArray[address, 30] list containing all guards
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
def get_all_campaign_addresses() -> DynArray[address, 30]:
    """
    @notice Get all campaign addresses
    @return DynArray[address, 20] list containing all campaign addresses
    """
    return self.campaign_addresses