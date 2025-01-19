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

deploy_info_taiko:
	ape run scripts/deploy_manager.py info --network taiko:mainnet:node

deploy_taiko:
	ape run scripts/deploy_manager.py deploy --network taiko:mainnet:node

deploy_many_single_campaigns_taiko:
	ape run scripts/deploy_manager.py deploy-many-single-campaigns --network taiko:mainnet:node

setup_op_campaign:
	ape run scripts/campaign_manager.py setup-op-campaign --network optimism:mainnet:node


import_pvk:
	ape accounts import arbideploy

networks_list:
	ape networks list

noisy_test:
	ape test -rP  --capture=no --network ethereum:local:test

test:
	ape test --network ethereum:local:test

