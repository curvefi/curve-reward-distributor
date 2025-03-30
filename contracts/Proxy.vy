# pragma version ^0.4.0
"""
@title Proxy
@author martinkrung for curve.fi
@license MIT
@notice Distributes variable rewards for one gauge through Distributor
"""


event NewProxy:
    proxy: address
    implementation: address
    timestamp: uint256


event MultipleNewProxy:
    proxies: DynArray[address, 27]
    implementation: address
    timestamp: uint256


interface ISProxy:
    def deploy_proxy(implementation: address) -> address: nonpayable


@external
def deploy_proxy(implementation: address) -> address:
    # Creates and returns the proxy address
    proxy: address = create_minimal_proxy_to(implementation)

    log NewProxy(proxy, implementation, block.timestamp)

    return proxy


@external
def deploy_multiple_proxies(
    implementation: address, n: uint256
) -> DynArray[address, 27]:
    # Creates and returns the proxy address
    proxies: DynArray[address, 27] = []

    for i: uint256 in range(n, bound=27):
        proxies.append(extcall ISProxy(self).deploy_proxy(implementation))

    log MultipleNewProxy(proxies, implementation, block.timestamp)

    return proxies
