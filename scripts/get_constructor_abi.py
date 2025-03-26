import os
from ape import project
from eth_abi import encode

GUARDS = os.getenv("GUARDS")
CRVUSD_ADDRESS = os.getenv("CRVUSD_ADDRESS")
EXECUTE_REWARD_AMOUNT = os.getenv("EXECUTE_REWARD_AMOUNT")


def get_constructor_args():
    guards = GUARDS.split(",")
    print("Guards:", guards)

    # Get constructor ABI
    constructor = next(
        item for item in project.SingleCampaign.contract_type.abi if item.type == "constructor"
    )

    # Get the constructor input types
    input_types = [arg.type for arg in constructor.inputs]
    constructor_args = [guards, CRVUSD_ADDRESS, int(EXECUTE_REWARD_AMOUNT)]

    # Encode the arguments
    encoded_args = encode(input_types, constructor_args)
    print("Encoded constructor arguments:", encoded_args.hex())


if __name__ == "__main__":
    get_constructor_args()
