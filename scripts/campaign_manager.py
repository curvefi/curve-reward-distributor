import os
import click
import time
import sys

from ape import project

from ape.cli import ConnectedProviderCommand, account_option

GUARDS = os.getenv('GUARDS')
REWARD_TOKEN = os.getenv('REWARD_TOKEN')
REWARD_TOKEN_DIGITS = os.getenv('REWARD_TOKEN_DIGITS')
RECOVERY_ADDRESS = os.getenv('RECOVERY_ADDRESS')
# EXISTING_TEST_GAUGE = os.getenv('EXISTING_TEST_GAUGE')

REWARD_TOKEN_TESTNET = os.getenv('REWARD_TOKEN_TESTNET')
GAUGE_ALLOWLIST = os.getenv('GAUGE_ALLOWLIST')

DEPLOYED_DISTRIBUTOR = os.getenv('DEPLOYED_DISTRIBUTOR')
DRY_RUN = os.getenv('DRY_RUN')
CAMPAIGN_CONTRACT_LIST = os.getenv('CAMPAIGN_CONTRACT_LIST')


@click.group()
def cli():
    pass

@click.command(cls=ConnectedProviderCommand)
@account_option()
def info(ecosystem, provider, account, network):
    click.echo(f"ecosystem: {ecosystem.name}")
    click.echo(f"network: {network.name}")
    click.echo(f"provider_id: {provider.chain_id}")
    click.echo(f"connected: {provider.is_connected}")
    click.echo(f"account: {account}")

cli.add_command(info)


@click.command(cls=ConnectedProviderCommand)
@account_option()
def setup_taiko_campaign(ecosystem, network, provider, account):
    if not DRY_RUN:
        account.set_autosign(True)

    min_epoch_duration = int(3.5 * 24 * 60 * 60)
    campaign_contract_list = CAMPAIGN_CONTRACT_LIST.split(",")
    amount_steady_epochs = 5  # 29 epochs = epoch is 1/2 week
    #amount_steady_epochs = 31  # 29 epochs = epoch is 1/2 week


    print("USDC/USDT: https://taikoscan.io/address/0xfdb6a782aAa9254fAb82eE39b3fd7728C8442f0D")

    campaign_address = campaign_contract_list.pop(0)   
    gauge_address = "0x79291f833bc0c8e06c5232144a9ac76faef261ab"

    growth_epochs = [300, 600, 1200]
    steady_epochs = [2100] * amount_steady_epochs 
    epochs = growth_epochs + steady_epochs

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

    print("crvUSD / USDT: https://taikoscan.io/address/0xdb23003932abca63b64422a29e11f9c58b9688f5")
    campaign_address = campaign_contract_list.pop(0)
    gauge_address = "0x538e5c90c75247f9978e4270f2fb22cfe86a8253"
    
    growth_epochs = [200, 400, 800]
    steady_epochs = [1400] * amount_steady_epochs
    epochs = growth_epochs + steady_epochs

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

    print("crvUSD/USDC : https://taikoscan.io/address/0xb74370f716f1d552684c98a8b4ddf9859960386c")
    campaign_address = campaign_contract_list.pop(0)
    gauge_address = "0x9ccd30a992ec6775ad4b95fc267e7fd28d7f52a9"

    growth_epochs = [200, 400, 800]
    steady_epochs = [1400] * amount_steady_epochs
    epochs = growth_epochs + steady_epochs

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)
    
    print("crvUSD/WBTC/WETH (Tricrypto-crvUSD) : https://taikoscan.io/address/0x51a910e5fde25a53d9b80b13d5e948e1a88b245f")
    campaign_address = campaign_contract_list.pop(0)
    gauge_address = "0xf536ee5567ef18c0ec3439b2f6dc67e8258e804c"

    growth_epochs = [300, 600, 1200]
    steady_epochs = [1400] * amount_steady_epochs 
    epochs = growth_epochs + steady_epochs

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

    print("crvUSD/CRV/Taiko (TriCRV-Taiko) : https://taikoscan.io/address/0x9511623fb1c793b875b490fc331df503108e9313")
    campaign_address = campaign_contract_list.pop(0)
    gauge_address = "0x5a673f07624cac33039b446a5f08cbb4482f6003"

    growth_epochs = [300, 600, 1200]
    steady_epochs = [2100] * amount_steady_epochs 
    epochs = growth_epochs + steady_epochs

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

    print("Savings crvUSD: https://taikoscan.io/address/0xc09d2e66c7f5ae67b03f4b32f59da8a08cddc50b")
    campaign_address = campaign_contract_list.pop(0)
    gauge_address = "0x0cb96b43fdd4074b85e6bf128d0103008bd63f15"

    growth_epochs = [200, 400, 800]
    steady_epochs = [1400] * amount_steady_epochs
    epochs = growth_epochs + steady_epochs

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)


cli.add_command(setup_taiko_campaign)


@click.command(cls=ConnectedProviderCommand)
@account_option()
def setup_arbitrum_campaign(ecosystem, network, provider, account):
    if not DRY_RUN:
        account.set_autosign(True)

    campaign_contract_list = CAMPAIGN_CONTRACT_LIST.split(",")

    # Import lending gauges from env
    GAUGE_LEND_ARB_LONG = os.getenv('GAUGE_LEND_ARB_LONG')
    GAUGE_CRVUSD_ARB_CRV = os.getenv('GAUGE_CRVUSD_ARB_CRV')
    GAUGE_CRVUSD_WBTC_WETH = os.getenv('GAUGE_CRVUSD_WBTC_WETH')

    min_epoch_duration = int(7 * 24 * 60 * 60)
    # ARB Long
    campaign_address = campaign_contract_list.pop(0)    
    gauge_address = GAUGE_LEND_ARB_LONG
    epochs = [200, 400, 600, 800, 600, 400, 200]

    # Set up campaign for gauge
    #setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

    # crvUSD/ARB/CRV (CRV-ARB)
    campaign_address = campaign_contract_list.pop(0)    
    gauge_address = GAUGE_CRVUSD_ARB_CRV
    epochs = [6000, 5800, 5600, 5400, 5200, 5000, 4800]

    # Set up campaign for gauge
    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

    # crvUSD/ARB/CRV (CRV-ARB)
    campaign_address = campaign_contract_list.pop(0)    
    gauge_address = GAUGE_CRVUSD_WBTC_WETH
    epochs = [2400, 2400, 2300, 2200, 2100, 2000, 1900]

    # Set up campaign for gauge
    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

cli.add_command(setup_arbitrum_campaign)

@click.command(cls=ConnectedProviderCommand)
@account_option()
def setup_op_campaign(ecosystem, network, provider, account):
    if not DRY_RUN:
        account.set_autosign(True)

    # Import lending gauges from env
    GAUGE_LEND_CRV_LONG = os.getenv('GAUGE_LEND_CRV_LONG')
    GAUGE_LEND_OP_LONG = os.getenv('GAUGE_LEND_OP_LONG') 
    GAUGE_LEND_WBTC_LONG = os.getenv('GAUGE_LEND_WBTC_LONG')
    GAUGE_LEND_WETH_LONG = os.getenv('GAUGE_LEND_WETH_LONG')
    GAUGE_LEND_WSTETH_LONG = os.getenv('GAUGE_LEND_WSTETH_LONG')
    GAUGE_TRICRYPTO_CRVUSD = os.getenv('GAUGE_TRICRYPTO_CRVUSD')
    GAUGE_TRICRV = os.getenv('GAUGE_TRICRV')
    GAUGE_WSTETH_ETH = os.getenv('GAUGE_WSTETH_ETH')
    GAUGE_SCRVUSD = os.getenv('GAUGE_SCRVUSD')

    campaign_contract_list = CAMPAIGN_CONTRACT_LIST.split(",")

    min_epoch_duration = int(7 * 24 * 60 * 60)
    # CRV/crvUSD Long
    print(f"***************************************************************")
    print("CRV/crvUSD Long")
    print(f"***************************************************************")
    campaign_address = campaign_contract_list.pop(0)    
    gauge_address = GAUGE_LEND_CRV_LONG
    epochs = [250, 1000, 1250, 1000, 750, 500, 250]

    # Set up campaign for gauge
    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

    # OP/crvUSD Long
    print(f"***************************************************************")
    print("OP/crvUSD Long")
    print(f"***************************************************************")
    campaign_address = campaign_contract_list.pop(0)
    gauge_address = GAUGE_LEND_OP_LONG
    # double the amount for OP/crvUSD Long
    # reverse order for OP/crvUSD Long
    epochs = [500, 2000, 2500, 2000, 1500, 1000, 500]

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

    # WBTC/crvUSD Long
    print(f"***************************************************************")
    print("WBTC/crvUSD Long")
    print(f"***************************************************************")
    campaign_address = campaign_contract_list.pop(0)
    gauge_address = GAUGE_LEND_WBTC_LONG
    epochs = [250, 1000, 1250, 1000, 750, 500, 250]

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)
    
    # ETH/crvUSD Long
    print(f"***************************************************************")
    print("ETH/crvUSD Long")
    print(f"***************************************************************")
    campaign_address = campaign_contract_list.pop(0)
    gauge_address = GAUGE_LEND_WETH_LONG
    epochs = [250, 1000, 1250, 1000, 750, 500, 250]

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

    # wsETH/crvUSD Long
    print(f"***************************************************************")
    print("wsETH/crvUSD Long")
    print(f"***************************************************************")
    campaign_address = campaign_contract_list.pop(0)
    gauge_address = GAUGE_LEND_WSTETH_LONG
    epochs = [250, 1000, 1250, 1000, 750, 500, 250]

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

    '''
    campaings for AMM
    '''

    # crvUSD/WBTC/WETH (Tricrypto-crvUSD)
    print(f"***************************************************************")
    print("crvUSD/WBTC/WETH (Tricrypto-crvUSD)")
    print(f"***************************************************************")
    campaign_address = campaign_contract_list.pop(0)
    gauge_address = GAUGE_TRICRYPTO_CRVUSD
    total_amm_epochs = 28  # 28 weeks

    epochs = [1071.42857] * total_amm_epochs  # Creates a list of x elements, each with the same value

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)


    # crvUSD/CRV/OP (TriCRV-Optimism)
    print(f"***************************************************************")
    print("crvUSD/CRV/OP (TriCRV-Optimism)")
    print(f"***************************************************************")
    campaign_address = campaign_contract_list.pop(0)
    gauge_address = GAUGE_TRICRV
    
    epochs = [2142.85714] * total_amm_epochs   # Creates a list of x elements, each with the same value

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

    # ETH/WSTEH
    print(f"***************************************************************")
    print("ETH/WSTEH")
    print(f"***************************************************************")
    campaign_address = campaign_contract_list.pop(0)
    gauge_address = GAUGE_WSTETH_ETH
    
    epochs = [714.28571] * total_amm_epochs   # Creates a list of x elements, each with the same value

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

    # crvUSD/scrvUSD 
    print(f"***************************************************************")
    print("crvUSD/scrvUSD")
    print(f"***************************************************************")
    campaign_address = campaign_contract_list.pop(0)
    gauge_address = GAUGE_SCRVUSD
    
    epochs = [357.14285] * total_amm_epochs   # Creates a list of x elements, each with the same value

    setup_campaign_for_gauge(campaign_address, gauge_address, min_epoch_duration, account)
    epochs = convert_to_digits(epochs, min_epoch_duration)
    set_reward_epochs_for_gauge(campaign_address, epochs, account)

cli.add_command(setup_op_campaign)


def setup_campaign_for_gauge(campaign_address, receiving_gauge, min_epoch_duration, account):

    if DRY_RUN:
        print(f"[DRY RUN]\nWould setup campaign: {campaign_address}\n"
              f"distributor: {DEPLOYED_DISTRIBUTOR}\n"
              f"gauge: {receiving_gauge}\n"
              f"min_epoch_duration: {min_epoch_duration}\n")
        return
        
    single_campaign = project.SingleCampaign.at(campaign_address)
    is_setup_complete = single_campaign.is_setup_complete()
    if is_setup_complete:
        print(f"Campaign already setup for campaign: {campaign_address}")
        return
    else:
        print(f"[DRY RUN]\nWould setup campaign: {campaign_address}\n"
            f"distributor: {DEPLOYED_DISTRIBUTOR}\n"
            f"gauge: {receiving_gauge}\n"
            f"min_epoch_duration: {min_epoch_duration}\n")
        single_campaign.setup(DEPLOYED_DISTRIBUTOR, receiving_gauge, min_epoch_duration, sender=account, max_priority_fee="10 wei", max_fee="0.1 gwei", gas_limit="400000", transaction_acceptance_timeout=300)
        print(f"Campaign setup complete for campaign: {campaign_address}")
    
def set_reward_epochs_for_gauge(campaign_address, epochs, account):
    epoch_sum = 0
    if DRY_RUN:
        print(f"[DRY RUN]\nWould set reward epochs for gauge: {campaign_address}\n")
        for i, epoch in enumerate(epochs):
            epoch_sum += epoch
            print(f"Epoch {i+1}: {epoch}; sum: {epoch_sum}")
        return
        
    single_campaign = project.SingleCampaign.at(campaign_address)
    is_reward_epochs_set = single_campaign.is_reward_epochs_set()
    if is_reward_epochs_set:
        print(f"Reward epochs already set for campaign: {campaign_address}")
        return
    else:
        print(f"Setting reward epochs for campaign: {campaign_address}\n")  
        for i, epoch in enumerate(epochs):
            epoch_sum += epoch
            print(f"Epoch {i+1}: {epoch}: sum: {epoch_sum}")
        single_campaign.set_reward_epochs(epochs, sender=account, max_priority_fee="10 wei", max_fee="0.1 gwei", gas_limit="400000", transaction_acceptance_timeout=300)
        print(f"Reward epochs set for campaign: {campaign_address}")

# Track total rewards across all conversions
_total_rewards = 0
_total_distribute_events = 0

def convert_to_digits(epochs: list, min_epoch_duration: int) -> list:
    global _total_rewards
    global _total_distribute_events
    epoch_sum = 0
    
    # Print epochs vertically for better readability

    converted = [int(x * 10**int(REWARD_TOKEN_DIGITS)) for x in epochs]
    print("Epochs")
    for i, epoch in enumerate(epochs):
        epoch_sum += epoch
        print(f"  Epoch {i+1}: {epoch}; sum: {epoch_sum}")
    
    _total_rewards += sum(converted)
    _total_distribute_events += len(epochs)
    runtime = len(epochs) * min_epoch_duration
    print(f"\nNumber of epochs: {len(epochs)}")
    print(f"First reward: {epochs[0]}")
    print(f"Last reward: {epochs[-1]}")
    print(f"Rewards sum this call: {sum(converted) / 10**int(REWARD_TOKEN_DIGITS):,.4f}")
    print(f"Runtime in days: {runtime/24/60/60}")
    print(f"Runtime in weeks: {runtime/24/60/60/7}")
    print(f"Total rewards per day: {_total_rewards / 10**int(REWARD_TOKEN_DIGITS) / (runtime/24/60/60):,.4f}")
    print(f"Total rewards per week: {_total_rewards / 10**int(REWARD_TOKEN_DIGITS) / (runtime/24/60/60/7):,.4f}")
    print(f"Total rewards allocated so far: {_total_rewards / 10**int(REWARD_TOKEN_DIGITS):,.4f}")
    print(f"Total distribute events: {_total_distribute_events}")
 
    return converted


@click.command(cls=ConnectedProviderCommand)
@account_option()
def set_reward_epochs(ecosystem, network, provider, account):

    #account.set_autosign(True)

    # Load existing SingleCampaign contract from address
    # USDC/USDT
    new_epochs = [1200 , 750, 600, 450]
    new_epochs = convert_to_digits(new_epochs)
    campaign_address = "0x5d42F882e478e4fdD09D41532B412F1aD60462aF"
    gauge_address = "0x79291F833bC0c8E06C5232144A9Ac76FAEf261Ab"
    single_campaign = project.SingleCampaign.at(campaign_address)

    # crvUSD / USDT
    # crvUSD/USDC
    # crvUSD/WBTC/WETH (Tricrypto-crvUSD)
    # crvUSD/CRV/Taiko (TriCRV-Taiko)
    # Savings crvUSD

    print(f"new_epochs: {new_epochs}")

    is_reward_epochs_set = single_campaign.is_reward_epochs_set()

    print(f"is_reward_epochs_set: {is_reward_epochs_set}")

    single_campaign.set_reward_epochs(new_epochs, sender=account)


    single_campaign.set_reward_epochs(new_epochs)

    is_reward_epochs_set = single_campaign.is_reward_epochs_set
    print(f"is_reward_epochs_set: {is_reward_epochs_set}")

    click.echo(f"ecosystem: {ecosystem.name}")
    click.echo(f"network: {network.name}")

    if ecosystem.name == 'arbitrum':
        max_fee = "10 gwei"
        blockexplorer = "https://sepolia.arbiscan.io"
    else:
        max_fee = "0.1 gwei"
        print("Using max fee of 0.1 gwei")
        blockexplorer = "https://taikoscan.io"


cli.add_command(set_reward_epochs)

@click.command(cls=ConnectedProviderCommand)
@account_option()
def run_next_taiko(account):
    # on taiko

    campaign_address = ["0xb74370F716f1D552684c98a8b4DDF9859960386c",
    "0x9cCd30A992EC6775ad4B95fc267e7Fd28d7f52A9", 
    "0x51A910e5fde25a53d9b80b13d5E948E1a88b245f", 
    "0xDB23003932abcA63b64422A29E11f9c58B9688F5", 
    "0xC09d2E66c7f5Ae67b03F4B32f59Da8A08cddc50B", 
    "0xfdb6a782aAa9254fAb82eE39b3fd7728C8442f0D",
    "0x9511623fB1C793B875B490FC331df503108E9313"]

    for address in campaign_address:
        single_campaign = project.SingleCampaign.at(address)
        next_epoch_info = single_campaign.get_next_epoch_info()
        DISTRIBUTION_BUFFER = single_campaign.DISTRIBUTION_BUFFER()
        print(f"DISTRIBUTION_BUFFER: {DISTRIBUTION_BUFFER}")
        print(f"next run in days: {next_epoch_info[1]/60/60/24}")
        print(f"next run in hours: {next_epoch_info[1]/60/60}")
        print(f"next run in seconds: {next_epoch_info[1]}")
        print(f"amount: {next_epoch_info[0]}")
        print(f"amount with decimals: {next_epoch_info[0]/10**18}")
        print(f"execution_allowed: {single_campaign.execution_allowed()}")
        # print(f"execution_allowed_time: {single_campaign.execution_allowed_time()}")
        # print(f"execution_allowed_time_buffer: {single_campaign.execution_allowed_time_buffer()}")
        if next_epoch_info[1]  < DISTRIBUTION_BUFFER:
            if single_campaign.execution_allowed():
                print(f"Next epoch info is less than 2 days for campaign: {address}")
                distribute_reward = single_campaign.distribute_reward(sender=account)
                print(f"distribute_reward: {distribute_reward}")    
                next_epoch_info = single_campaign.get_next_epoch_info()
                print(f"next_epoch_info: {next_epoch_info}")
        else:
            print(f"Nothing executed for campaign, to early or outside of buffer time")

cli.add_command(run_next_taiko)


def setup(ecosystem, network):

    click.echo(f"ecosystem: {ecosystem.name}")
    click.echo(f"network: {network.name}")


    if ecosystem.name == 'arbitrum':
        max_fee = "1 gwei"
        blockexplorer = "https://sepolia.arbiscan.io"
    elif ecosystem.name == 'taiko':
        max_fee = "0.1 gwei"
        blockexplorer = "https://taikoscan.io"
    else:
        max_fee = "0.1 gwei"
        blockexplorer = "https://sepolia.arbiscan.io"
    return max_fee, blockexplorer