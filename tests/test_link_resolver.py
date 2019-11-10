import pytest
import voluptuous
from copy import deepcopy

from rules.link_resolver import rule as Rule

ruleconfig = {
    "name": "Test rule",
    "type": "test_type",
    "blocked": ["evilsi\\.te", "heresa\\.porn\\.domain"],
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

def test_evil_report(requests_mock, rule, report):
    # multiple statuses with one malicious
    rpt = report(
        statuses=[
            {
                "content":
                "<p>blah blah blah asdjhlg</p>"
            },
            {
                "content":
                '<p>heres an <a href="https://example.com/archive/notmaliciousatall/">inconspicuous archive link</a></p>'
            }
        ]
    )
    requests_mock("head", {}, url="https://heresa.porn.domain")
    assert rule.test_report(rpt)

def test_good_report(requests_mock, rule, report):
    # multiple statuses with one malicious
    rpt = report(
        statuses=[
            {
                "content":
                "<p>blah blah blah asdjhlg</p>"
            },
            {
                "content":
                '<p>heres an <a href="https://example.com/archive/actuallynotmalicious/">actually ok archive link</a></p>'
            }
        ]
    )
    requests_mock("head", {}, url="https://good.website")
    assert not rule.test_report(rpt)
