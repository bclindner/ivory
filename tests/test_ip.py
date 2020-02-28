import pytest
import voluptuous
from copy import deepcopy

from rules.ip import rule as Rule

ruleconfig = {
    "name": "Test rule",
    "type": "ip",
    "blocked": ["1.1.1.1", "8.8.8.8"],
    "severity": 1,
    "punishment": {
            "type": "reject"
    }
}


@pytest.fixture
def rule():
    return Rule(ruleconfig)

def test_requires_blocked():
    bad_config = deepcopy(ruleconfig)
    bad_config.pop("blocked")
    # bad config no have block. no worky :(
    with pytest.raises(voluptuous.error.MultipleInvalid):
        Rule(bad_config)

def test_evil_pending_account(rule, pending_account):
    acct1 = pending_account(ip="1.1.1.1")
    assert rule.test_pending_account(acct1)
    acct2 = pending_account(ip="8.8.8.8")
    assert rule.test_pending_account(acct2)

def test_good_pending_account(rule, pending_account):
    acct = pending_account() # defaults to 127.0.0.1. good enough
    assert not rule.test_pending_account(acct)

