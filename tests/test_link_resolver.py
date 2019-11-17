import pytest
import voluptuous
import requests
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

@pytest.fixture
def head_mock(MockResponse, monkeypatch):
    def handler(url, *args, **kwargs):
        respmap = {
            "https://example.com/archive/notmaliciousatall/": "https://evilsi.te", # malicious site
            "https://example.com/archive/definitelynotporn/": "https://heresa.porn.domain", # malicious site
            "https://example.com/archive/actuallynotmalicious/": "https://example.com" # non-malicious site
        }
        return MockResponse(url=respmap[url])
    monkeypatch.setattr(requests, "head", handler)


def test_requires_blocked():
    bad_config = deepcopy(ruleconfig)
    bad_config.pop("blocked")
    # bad config no have block. no worky :(
    with pytest.raises(voluptuous.error.MultipleInvalid):
        Rule(bad_config)

def test_evil_report(head_mock, rule, report):
    # multiple statuses with one malicious
    rpt1 = report(
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
    assert rule.test_report(rpt1)
    rpt2 = report(
        statuses=[
            {
                "content":
                '<p>yeah uhh <a href="https://example.com/archive/definitelynotporn/">im up to no good lol</a></p>'
            }
        ]
    )
    assert rule.test_report(rpt2)

def test_good_report(head_mock, rule, report):
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
    assert not rule.test_report(rpt)
