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
def sfs_mock(requests_mock):
    """
    Expose a way to mock the "requests" library so that we can test inputs.
    """
    def _sfs_mock(**mock_kwargs):
            # The rule currently only uses confidence internally, but we
            # simulate a full response just in case
            ip = {
                "frequency": 10,
                "appears": 1
            }
            ip_conf = mock_kwargs.get('ip_confidence')
            if ip_conf:
                ip['confidence'] = ip_conf
            email = {
                "frequency": 10,
                "appears": 1
            }
            email_conf = mock_kwargs.get('email_confidence')
            if email_conf:
                email['confidence'] = email_conf
            requests_mock("get", {
                "success": 1,
                "ip": ip,
                "email": email
            })
    return _sfs_mock

def test_requires_threshold():
    bad_config = deepcopy(ruleconfig)
    bad_config.pop("threshold")
    # bad config no have threshold. no worky :(
    with pytest.raises(voluptuous.error.MultipleInvalid):
        Rule(bad_config)

def test_evil_pending_account_iponly(rule, pending_account, sfs_mock):
    acct = pending_account()
    sfs_mock(ip_confidence=90)
    assert rule.test_pending_account(acct)

def test_good_pending_account_iponly(rule, pending_account, sfs_mock):
    acct = pending_account()
    # probably not *actually* good but not confident enough for us to act on,
    # of course
    sfs_mock(ip_confidence=89)
    assert not rule.test_pending_account(acct)

def test_evil_pending_account_emailonly(rule, pending_account, sfs_mock):
    acct = pending_account()
    sfs_mock(email_confidence=90)
    assert rule.test_pending_account(acct)

def test_good_pending_account_emailonly(rule, pending_account, sfs_mock):
    acct = pending_account()
    sfs_mock(email_confidence=89)
    assert not rule.test_pending_account(acct)

def test_evil_pending_account(rule, pending_account, sfs_mock):
    acct = pending_account()
    sfs_mock(ip_confidence=85, email_confidence=99)
    assert rule.test_pending_account(acct)

def test_good_pending_account(rule, pending_account, sfs_mock):
    acct = pending_account()
    sfs_mock(ip_confidence=80, email_confidence=89)
    assert not rule.test_pending_account(acct)
