import pytest
import voluptuous
import requests # for mocking
from copy import deepcopy

from rules.stopforumspam import rule as Rule

ruleconfig = {
        "name": "StopForumSpam test",
        "type": "stopforumspam",
        "threshold": 90,
        "severity": 1,
        "punishment": {
          "type": "reject"
        }
      }


@pytest.fixture
def rule():
    return Rule(ruleconfig)

@pytest.fixture
def sfs_response():
    def _sfs_response(ip_conf=None, email_conf=None):
        # The rule currently only uses confidence internally, but we
        # simulate a full response just in case
        resp = {
            "success": 1,
            "ip": {
                "frequency": 10,
                "appears": 1
            },
            "email": {
                "frequency": 10,
                "appears": 1
            }
        }
        if ip_conf:
            resp['ip']['confidence'] = ip_conf
        if email_conf:
            resp['email']['confidence'] = email_conf
        return resp
    return _sfs_response

@pytest.fixture
def sfs_mock(monkeypatch, MockResponse, sfs_response):
    """
    Expose a way to mock the "requests" library so that we can test inputs.
    """
    def _sfs_mock(ip=None, email=None):
        def handler(*args, **kwargs):
            return MockResponse(json=sfs_response(ip, email))
        monkeypatch.setattr(requests, "get", handler)
    return _sfs_mock

def test_requires_threshold():
    bad_config = deepcopy(ruleconfig)
    bad_config.pop("threshold")
    # bad config no have threshold. no worky :(
    with pytest.raises(voluptuous.error.MultipleInvalid):
        Rule(bad_config)

def test_evil_pending_account_iponly(rule, pending_account, sfs_mock):
    acct = pending_account()
    sfs_mock(ip=90)
    assert rule.test_pending_account(acct)

def test_good_pending_account_iponly(rule, pending_account, sfs_mock):
    acct = pending_account()
    # probably not *actually* good but not confident enough for us to act on,
    # of course
    sfs_mock(ip=89)
    assert not rule.test_pending_account(acct)

def test_evil_pending_account_emailonly(rule, pending_account, sfs_mock):
    acct = pending_account()
    sfs_mock(email=90)
    assert rule.test_pending_account(acct)

def test_good_pending_account_emailonly(rule, pending_account, sfs_mock):
    acct = pending_account()
    sfs_mock(email=89)
    assert not rule.test_pending_account(acct)

def test_evil_pending_account(rule, pending_account, sfs_mock):
    acct = pending_account()
    sfs_mock(ip=85, email=99)
    assert rule.test_pending_account(acct)

def test_good_pending_account(rule, pending_account, sfs_mock):
    acct = pending_account()
    sfs_mock(ip=80, email=89)
    assert not rule.test_pending_account(acct)
