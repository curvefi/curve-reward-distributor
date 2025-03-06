all:

start_env:
	# source will not work, but this is for cmd documentation
	source .env
	source .venv/bin/activate

deploy_info:
	ape run scripts/deploy_manager.py info --network arbitrum:mainnet-fork:foundry

deploy_local:
	ape run scripts/deploy_manager.py deploy --network arbitrum:mainnet-fork:foundry

deploy_single_campaign_local:
	ape run scripts/deploy_manager.py deploy-single-campaign --network arbitrum:mainnet-fork:foundry

deploy_single_campaign_arbitrum_sepolia:
	ape run scripts/deploy_manager.py deploy-single-campaign --network arbitrum:sepolia:infura

deploy_single_campaign_taiko:
	ape run scripts/deploy_manager.py deploy-single-campaign --network taiko:mainnet:node

get_constructor_abi:
	python  scripts/get_constructor_abi.py

deploy_arbitrum_sepolia:
	ape run scripts/deploy_manager.py deploy --network arbitrum:sepolia:infura

deploy_arbitrum:
	ape run scripts/deploy_manager.py deploy --network arbitrum:mainnet:infura

rune_next_arbi_epoch:
	ape run scripts/campaign_manager.py run-next-arbi --network arbitrum:mainnet:infura

deploy_info_taiko:
	ape run scripts/deploy_manager.py info --network taiko:mainnet:node

deploy_taiko:
	ape run scripts/deploy_manager.py deploy --network taiko:mainnet:node

deploy_many_campaigns_taiko:
	ape run scripts/deploy_manager.py deploy-many-campaigns  --network taiko:mainnet:node

setup_taiko_campaign:
	ape run scripts/campaign_manager.py setup-taiko-campaign --network taiko:mainnet:node

setup_op_campaign:
	ape run scripts/campaign_manager.py setup-op-campaign --network optimism:mainnet:node

deploy_many_campaigns_optimism:
	ape run scripts/deploy_manager.py deploy-many-campaigns  --network optimism:mainnet:node


rune_next_taiko_epoch:
	ape run scripts/campaign_manager.py run-next-taiko --network taiko:mainnet:node

import_pvk:
	ape accounts import arbideploy

networks_list:
	ape networks list

noisy_test:
	ape test -rP  --capture=no --network ethereum:local:test

single_test:
	# Usage: make single_test t=test_remove_active_campaign_address_revert_not_guard
	ape test tests/SingleCampaign/test_single_campaign.py -k "$(t)" --network ethereum:local:test

test:
	ape test --network ethereum:local:test
