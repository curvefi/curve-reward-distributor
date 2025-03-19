import os
import click
import time

from dotenv import load_dotenv, dotenv_values

from ape import project
from ape.cli import ConnectedProviderCommand, account_option

# Load environment variables from .env_xx
#env_vars = dotenv_values(".env_sonic")

from scripts.get_constructor_abi_campaign import get_constructor_args


GUARDS = os.getenv('GUARDS')
GUARDS_AND_CAMPAIGNS = os.getenv('GUARDS_AND_CAMPAIGNS')
REWARD_TOKEN = os.getenv('REWARD_TOKEN')
RECOVERY_ADDRESS = os.getenv('RECOVERY_ADDRESS')
# EXISTING_TEST_GAUGE = os.getenv('EXISTING_TEST_GAUGE')

# GAUGE_ALLOWLIST = os.getenv('GAUGE_ALLOWLIST')
PASSTROUGH_GAUGE_ALLOWLIST = os.getenv('PASSTROUGH_GAUGE_ALLOWLIST')

CRVUSD_ADDRESS = os.getenv('CRVUSD_ADDRESS')
EXECUTE_REWARD_AMOUNT = os.getenv('EXECUTE_REWARD_AMOUNT')
DRY_RUN = os.getenv('DRY_RUN')

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
def deploy(ecosystem, network, provider, account):
    account.set_autosign(True)
   
    max_fee, blockexplorer = setup(ecosystem, network)

    """
    if EXISTING_TEST_GAUGE is None:
        test_gauge = account.deploy(project.TestGauge, REWARD_TOKEN, RECOVERY_ADDRESS, max_priority_fee="100 wei", max_fee=max_fee, gas_limit="100000")
    else:
        test_gauge = EXISTING_TEST_GAUGE

    gauges.append(recovery_gauge)
    """
 
    gauges = PASSTROUGH_GAUGE_ALLOWLIST.split(",")
    click.echo(gauges)
    guards = GUARDS_AND_CAMPAIGNS.split(",")
    click.echo(guards)

    deploy = account.deploy(project.Distributor, guards, REWARD_TOKEN, gauges, RECOVERY_ADDRESS, max_priority_fee="10 wei", max_fee=max_fee, gas_limit="400000")

cli.add_command(deploy)

@click.command(cls=ConnectedProviderCommand)
@account_option()
def deploy_campaign_proxy(ecosystem, network, provider, account):
    account.set_autosign(True)

    max_fee, blockexplorer = setup(ecosystem, network)

    deploy = account.deploy(project.Proxy, 0x9d45a61acA552F49D3998906d4112ae75c130d76, max_priority_fee="10 wei", max_fee=max_fee, gas_limit="400000")

cli.add_command(deploy_campaign_proxy)



@click.command(cls=ConnectedProviderCommand)
@account_option()
def deploy_single_campaign(ecosystem, network, provider, account):
    account.set_autosign(True)

    max_fee, blockexplorer = setup(ecosystem, network)

    guards = GUARDS.split(",")
    single_campaign = account.deploy(project.SingleCampaign, guards, CRVUSD_ADDRESS, EXECUTE_REWARD_AMOUNT, max_priority_fee="1000 wei", max_fee=max_fee, gas_limit="1000000")

    click.echo(single_campaign)

cli.add_command(deploy_single_campaign)

@click.command(cls=ConnectedProviderCommand)
@account_option()
def deploy_many_campaigns(ecosystem, network, provider, account):
    print(f"DRY_RUN: {DRY_RUN}")
    if not DRY_RUN:
        account.set_autosign(True)

    max_fee, blockexplorer = setup(ecosystem, network)

    guards = GUARDS.split(",")
    single_campaign_contracts = []

    for i in range(10):
        if not DRY_RUN:
            single_campaign = account.deploy(project.SingleCampaign, guards, CRVUSD_ADDRESS, CRVUSD_ADDRESS, max_priority_fee="1000 wei", max_fee=max_fee, gas_limit="1000000")
            get_constructor_args(guards, CRVUSD_ADDRESS, EXECUTE_REWARD_AMOUNT)
            single_campaign_address = single_campaign.address
        else:
            get_constructor_args(guards, CRVUSD_ADDRESS, EXECUTE_REWARD_AMOUNT)

            single_campaign_address = "0x_dry_run"

        single_campaign_contracts.append(single_campaign_address)

        # Log contract address and transaction info
        with open(f"logs/single_campaign_contracts_{ecosystem.name}.log", "a+") as f:
            f.write(f"Single Campaign Contract: {single_campaign_address}\n")
            f.write(f"Link: {blockexplorer}/address/{single_campaign_address}\n")
            f.write(f"Single Campaign Contract List \n {[str(contract) for contract in single_campaign_contracts]}\n")
            f.write(f"{','.join(str(contract) for contract in single_campaign_contracts)}\n")
            f.write("-" * 80 + "\n\n")

        # Sleep for 1 second between deployments
        if not DRY_RUN:
            time.sleep(2)

    click.echo(single_campaign_contracts)
    click.echo(single_campaign_address)

cli.add_command(deploy_many_campaigns)


def setup(ecosystem, network):

    click.echo(f"ecosystem: {ecosystem.name}")
    click.echo(f"network: {network.name}")

    if ecosystem.name == 'arbitrum':
        max_fee = "0.1 gwei"
        if network.name == 'sepolia':
            blockexplorer = "https://sepolia.arbiscan.io"
        else:
            blockexplorer = "https://arbiscan.io"
    elif ecosystem.name == 'optimism':
        max_fee = "0.0001 gwei"
        blockexplorer = "https://optimistic.etherscan.io"
    elif ecosystem.name == 'taiko':
        if network.name == 'sepolia':   
            max_fee = "0.01 gwei"
            blockexplorer = "https://testnet.sonicscan.org"
        else:
            max_fee = "0.01 gwei"
            blockexplorer = "https://taikoscan.io"

    elif ecosystem.name == 'sonic':
        max_fee = "66 gwei"
        blockexplorer = "https://sonicscan.org/"
    else:
        max_fee = "0.1 gwei"
        blockexplorer = "https://sepolia.arbiscan.io"
    return max_fee, blockexplorer
