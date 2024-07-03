# This script is only useful if you use the Akash's CLI.

# Wallet name.
export AKASH_KEY_NAME=

# Where the keys are stored.
export AKASH_KEYRING_BACKEND=os

# Account address.
export AKASH_ACCOUNT_ADDRESS="$(provider-services keys show $AKASH_KEY_NAME -a)"

# Base network URL.
export AKASH_NET="https://raw.githubusercontent.com/akash-network/net/main/mainnet"

# Akash version of the network.
export AKASH_VERSION="$(curl -s https://api.github.com/repos/akash-network/provider/releases/latest | jq -r '.tag_name')"

# Akash chain-id.
export AKASH_CHAIN_ID="$(curl -s "$AKASH_NET/chain-id.txt")"

# Akash node to connect to.
export AKASH_NODE="$(curl -s "$AKASH_NET/rpc-nodes.txt" | shuf -n 1)"

# Others.
export AKASH_GAS=auto
export AKASH_GAS_ADJUSTMENT=1.25
export AKASH_GAS_PRICES=0.025uakt
export AKASH_SIGN_MODE=amino-json

echo "*** Akash env vars has been set ***"
echo "AKASH_NODE: \"$AKASH_NODE\""
echo "AKASH_CHAIN_ID: \"$AKASH_CHAIN_ID\""
echo "AKASH_KEYRING_BACKEND: \"$AKASH_KEYRING_BACKEND\""

