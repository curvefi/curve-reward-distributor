def test_approve(alice, bob, reward_token):
    reward_token.approve(alice, 2**256 - 1, sender=bob)
    assert reward_token.allowance(bob, alice) == 2**256 - 1
