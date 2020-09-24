import pytest
import voluptuous
from copy import deepcopy

from rules.blank_signup import rule as Rule

ruleconfig = {
    "name": "Test rule",
    "type": "test_type",
    "severity": 1,
    "punishment": {
        "type": "reject"
    }
}


@pytest.fixture
def rule():
    return Rule(ruleconfig)

def test_evil_no_invite_pending_account(rule, pending_account_no_invite):
    acct = pending_account_no_invite()
    assert rule.test_pending_account(acct)

def test_evil_pending_account(rule, pending_account):
    acct2 = pending_account(message="")
    assert rule.test_pending_account(acct2)

def test_good_pending_account(rule, pending_account):
    acct = pending_account(message="this seems like a nice instance!")
    assert not rule.test_pending_account(acct)

