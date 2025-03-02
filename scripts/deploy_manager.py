import os
import click
import time

from ape import project

from ape.cli import ConnectedProviderCommand, account_option

GUARDS = os.getenv('GUARDS')
GUARDS_AND_CAMPAIGNS = os.getenv('GUARDS_AND_CAMPAIGNS')
REWARD_TOKEN = os.getenv('REWARD_TOKEN')
RECOVERY_ADDRESS = os.getenv('RECOVERY_ADDRESS')
# EXISTING_TEST_GAUGE = os.getenv('EXISTING_TEST_GAUGE')

REWARD_TOKEN_TESTNET = os.getenv('REWARD_TOKEN_TESTNET')
GAUGE_ALLOWLIST = os.getenv('GAUGE_ALLOWLIST')

DEPLOYED_DISTRIBUTOR = os.getenv('DEPLOYED_DISTRIBUTOR')
CRVUSD_ADDRESS = os.getenv('CRVUSD_ADDRESS')
EXECUTE_REWARD_AMOUNT = os.getenv('EXECUTE_REWARD_AMOUNT')
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
 
    gauges = GAUGE_ALLOWLIST.split(",")
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
def deploy_campaigns_with_many_proxies(ecosystem, network, provider, account):
    account.set_autosign(True)

    max_fee, blockexplorer = setup(ecosystem, network)

    guards = GUARDS.split(",")

    single_campaign = account.deploy(project.SingleCampaign, guards, CRVUSD_ADDRESS, EXECUTE_REWARD_AMOUNT, max_priority_fee="1000 wei", max_fee=max_fee, gas_limit="1000000")
       
    click.echo(single_campaign)

    proxy = account.deploy(project.Proxy, max_priority_fee="10 wei", max_fee=max_fee, gas_limit="400000")
    click.echo(proxy)

    single_campaign_contracts = []
    
    for i in range(25):
        proxy_campaign_address = proxy.deploy_proxy(single_campaign, max_priority_fee="10 wei", max_fee=max_fee, gas_limit="400000", sender=account)
        print(f"Campaign setup complete for campaign: {i} {proxy_campaign_address}")        
        
        single_campaign_contracts.append(proxy_campaign_address)

        with open("single_campaign_contracts.log", "a+") as f:
            f.write(f"Single Campaign: {single_campaign}\n")
            f.write(f"Single Campaign Proxy: {proxy_campaign_address}\n")
            f.write(f"Link: {blockexplorer}/address/{proxy_campaign_address}\n")
            f.write(f"Single Campaign Contract List: {[str(contract) for contract in single_campaign_contracts]}\n")
            f.write(f"{','.join(str(contract) for contract in single_campaign_contracts)}\n")
            f.write("-" * 80 + "\n")

        time.sleep(61)
        
cli.add_command(deploy_campaigns_with_many_proxies)


@click.command(cls=ConnectedProviderCommand)
@account_option()
def deploy_campaigns_with_many_proxies_no_loop(ecosystem, network, provider, account):
    account.set_autosign(True)

    max_fee, blockexplorer = setup(ecosystem, network)

    guards = GUARDS.split(",")

    single_campaign = account.deploy(project.SingleCampaign, guards, CRVUSD_ADDRESS, EXECUTE_REWARD_AMOUNT, max_priority_fee="1000 wei", max_fee=max_fee, gas_limit="1000000")
       
    click.echo(single_campaign)

    proxy = account.deploy(project.Proxy, max_priority_fee="10 wei", max_fee=max_fee, gas_limit="400000")
    click.echo(proxy)

    single_campaign_contracts = []
    n = 20

    proxy_campaign_addresses = proxy.deploy_multiple_proxies(single_campaign, n, max_priority_fee="10 wei", max_fee=max_fee, gas_limit="400000", sender=account)
    print(f"Campaign setup complete for campaign: {proxy_campaign_addresses}")        
    
    single_campaign_contracts.append(proxy_campaign_addresses)

    with open("single_campaign_contracts.log", "a+") as f:
        f.write(f"Single Campaign: {single_campaign}\n")
        f.write(f"Single Campaign Proxy: {proxy_campaign_addresses}\n")
        f.write(f"Link: {blockexplorer}/address/{proxy_campaign_addresses}\n")
        f.write(f"Single Campaign Contract List: {[str(contract) for contract in proxy_campaign_addresses]}\n")
        f.write(f"{','.join(str(contract) for contract in single_campaign_contracts)}\n")
        f.write("-" * 80 + "\n")
        
cli.add_command(deploy_campaigns_with_many_proxies_no_loop)

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

@click.command(cls=ConnectedProviderCommand)
@account_option()
def deploy_many_campaigns(ecosystem, network, provider, account):
    account.set_autosign(True)
    max_fee, blockexplorer = setup(ecosystem, network)

    guards = GUARDS.split(",")
    single_campaign_contracts = []

    for i in range(20):
        single_campaign = account.deploy(project.SingleCampaign, guards, CRVUSD_ADDRESS, EXECUTE_REWARD_AMOUNT, max_priority_fee="1000 wei", max_fee=max_fee, gas_limit="1000000")

        single_campaign_contracts.append(single_campaign)

        # Log contract address and transaction info
        with open("single_campaign_contracts.log", "a+") as f:
            f.write(f"Single Campaign Contract: {single_campaign.address}\n")
            f.write(f"Link: {blockexplorer}/address/{single_campaign.address}\n")
            f.write(f"Single Campaign Contract List: {[str(contract) for contract in single_campaign_contracts]}\n")
            f.write(f"{','.join(str(contract) for contract in single_campaign_contracts)}\n")
            f.write("-" * 80 + "\n")

        # Sleep for 1 second between deployments
     
        time.sleep(10)

    click.echo(single_campaign_contracts)
    click.echo(single_campaign)

cli.add_command(deploy_many_campaigns)