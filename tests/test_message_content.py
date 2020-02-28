import pytest
import voluptuous
from copy import deepcopy

from rules.message_content import rule as Rule

ruleconfig = {
    "name": "Test rule",
    "type": "message_content",
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
    rpt1 = report(
        statuses=[
            {
                "content":
                "<p>this post doesnt have anything objectionable in it haha</p>"
            },
            {
                "content":
                "<p>this post contains a badword ban me pls</p>"
            }
        ]
    )
    rpt2 = report(
        statuses=[
            {
                "content":
                "<p>this post doesnt have anything objectionable in it haha</p>"
            },
            {
                "content":
                "<p>slurslurslurslurslur</p>"
            }
        ]
    )
    assert rule.test_report(rpt1)
    assert rule.test_report(rpt2)

def test_good_report(rule, report):
    rpt = report(
        statuses=[
            {
                "content":
                "<p>blah blah slurp asdjhlg</p>"
            },
            {
                "content":
                "<p>im just fuckibg POSTING,,,</p>"
            }
        ]
    )
    assert not rule.test_report(rpt)

def test_evil_pending_account(rule, pending_account):
    acct1 = pending_account(message="lol slur slur slur you'll still let me in do it u wont")
    assert rule.test_pending_account(acct1)
    acct2 = pending_account(message="buy badword penis pills :joylmfao:")
    assert rule.test_pending_account(acct2)

def test_good_pending_account(rule, pending_account):
    acct = pending_account(message="slurpeedrinker26") # of no relation to slurpeedrinker28
    assert not rule.test_pending_account(acct)

