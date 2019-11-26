import pytest
import voluptuous
from copy import deepcopy

from rules.link_content import rule as Rule

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


def test_evil_report(rule, report):
    rpt1 = report(
        statuses=[
            {
                "content":
                '<p>this post doesnt have any objectionable <a href="http://example.com">links</a> in it haha</p>'
            },
            {
                "content":
                '<p>this post contains an <a href="https://heresa.porn.domain">bad link</a> ban me pls</p>'
            }
        ]
    )
    rpt2 = report(
        statuses=[
            {
                "content":
                "<p>this post doesnt have any links at all in it haha</p>"
            },
            {
                "content":
                '<p><a href="evilsi.te">gottem</a></p>'
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
                "<p>blah blah blah asdjhlg</p>"
            },
            {
                "content":
                '<p>check my mixtape <a href="https://soundcloud.com/">yeet</a></p>'
            }
        ]
    )
    assert not rule.test_report(rpt)
