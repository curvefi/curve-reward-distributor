python3.18 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install eth-ape'[recommended-plugins]'
pip install titanoboa
ape plugins install arbitrum
ape test
