import pytest
import voluptuous
from copy import deepcopy

from rules.username_content import rule as Rule

ruleconfig = {
    "name": "Test rule",
    "type": "username_content",
    # this second one will block "slur" but not "slurp".
    # just gotta be sure regex is working
    "blocked": ["badword", "slur[^p]"],
    "severity": 1,
    "punishment": {
            "type": "suspend"
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


def test_evil_report(rule, report):
    # In the rule itself we're actually using the one in the nested account
    # object (not the admin account) but we set both here for completion's
    # sake.
    rpt1 = report(
        reported={
            "username": "slurmaster9000",
            "account": {
                "username": "slurmaster9000"
            }
        }
    )
    rpt2 = report(
        reported={
            "username": "xX_badword_Xx",
            "account": {
                "username": "xX_badword_Xx"
            }
        }
    )
    assert rule.test_report(rpt1)
    assert rule.test_report(rpt2)

def test_good_report(rule, report):
    rpt = report(
        reported={
            # ffs corporate shill
            "username": "slurpeedrinker28",
            "account": {
                "username": "slurpeedrinker28"
            }
        }
    )
    assert not rule.test_report(rpt)

def test_evil_pending_account(rule, pending_account):
    acct1 = pending_account(username="slurtroll")
    assert rule.test_pending_account(acct1)
    acct2 = pending_account(username="badwordyfiend")
    assert rule.test_pending_account(acct2)

def test_good_pending_account(rule, pending_account):
    acct = pending_account(message="slurpeedrinker26") # of no relation to slurpeedrinker28
    assert not rule.test_pending_account(acct)

