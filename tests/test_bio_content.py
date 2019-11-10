import pytest
import voluptuous
from copy import deepcopy

from rules.bio_content import rule as Rule

ruleconfig = {
    "name": "Test rule",
    "type": "test_type",
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
        reported={
            "account": {
                "note": "slur!" # needs the extra char on the end for the regex hehe
            }
        }
    )
    rpt2 = report(
        reported={
            "account": {
                "fields": [
                    {
                        "name": "normal field",
                        "value": "just passing through here,,,,,"
                    }, {
                        "name": "bad field",
                        "value": "badword"
                    }
                ]
            }
        }
    )
    # test that it's checking the notes
    assert rule.test_report(rpt1)
    # test that it's checking the fields
    assert rule.test_report(rpt2)


def test_good_report(rule, report):
    rpt = report(
        reported={
            "username": "babword",
            "note": "slurpy boi",
            "fields": [
                {
                    "name": "website",
                    "value": "slurpzo.ne"
                }
            ]
        }
    )
    assert not rule.test_report(rpt)
