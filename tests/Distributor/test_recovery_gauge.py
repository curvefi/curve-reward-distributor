def test_test_gauge_reward_token(test_gauge, reward_token):
    assert test_gauge.reward_token() == reward_token


def test_test_gauge_recovery_address(diana, test_gauge):
    assert test_gauge.recovery_address() == diana


def test_test_gauge_deposit_reward_token(bob, test_gauge, reward_token):
    balance = reward_token.balanceOf(bob)
    assert reward_token.approve(test_gauge, balance, sender=bob)
    print(balance)
    test_gauge.deposit_reward_token(reward_token, balance, sender=bob)


def test_test_gauge_recover_token(alice, bob, diana, test_gauge, reward_token):
    balance = reward_token.balanceOf(bob)
    assert reward_token.approve(test_gauge, balance, sender=bob)
    test_gauge.deposit_reward_token(reward_token, balance, sender=bob)

    assert test_gauge.recover_token(sender=alice)
    balance_recoverd = reward_token.balanceOf(diana, sender=alice)
    assert balance_recoverd == balance
