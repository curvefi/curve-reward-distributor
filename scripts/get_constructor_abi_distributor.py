import os
import click
from ape import project
from eth_abi import encode

GUARDS = os.getenv('GUARDS_AND_CAMPAIGNS')
REWARD_TOKEN = os.getenv('REWARD_TOKEN')
PASSTROUGH_GAUGE_ALLOWLIST = os.getenv('PASSTROUGH_GAUGE_ALLOWLIST')
RECOVERY_ADDRESS = os.getenv('RECOVERY_ADDRESS')

def get_constructor_args():
    guards = GUARDS.split(",")
    print("Guards:", guards)
    gauges = PASSTROUGH_GAUGE_ALLOWLIST.split(",")
    print("Gauges:", gauges)

    # Get constructor ABI
    constructor = next(item for item in project.Distributor.contract_type.abi if item.type == 'constructor')

    # Get the constructor input types
    input_types = [arg.type for arg in constructor.inputs]
    constructor_args = [guards, REWARD_TOKEN, gauges, RECOVERY_ADDRESS]

    # Encode the arguments
    encoded_args = encode(input_types, constructor_args)
    print("Encoded constructor arguments:", encoded_args.hex())


if __name__ == "__main__":
    get_constructor_args()