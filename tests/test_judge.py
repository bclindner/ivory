import pytest
from judge import ReportJudge, PendingAccountJudge
from rules.message_content import Rule as MessageContentRule
from rules.username_content import Rule as UsernameContentRule

@pytest.fixture
def pendingjudge():
    return PendingAccountJudge([
      {
        "name": "Rule 1",
        "type": "username_content",
        "blocked": ["evilusername", "malicious", "asshole"],
        "severity": 1,
        "punishment": {
          "type": "silence"
        }
      },
      {
        "name": "Rule 2",
        "type": "message_content",
        "blocked": ["heck", "badword", "slur[^p]"],
        "severity": 5,
        "punishment": {
          "type": "suspend"
        }
      }
    ])


@pytest.fixture
def reportjudge():
    return ReportJudge([
      {
        "name": "Rule 1",
        "type": "username_content",
        "blocked": ["evilusername", "malicious", "asshole"],
        "severity": 1,
        "punishment": {
          "type": "silence"
        }
      },
      {
        "name": "Rule 2",
        "type": "message_content",
        "blocked": ["heck", "badword", "slur[^p]"],
        "severity": 5,
        "punishment": {
          "type": "suspend"
        }
      }
    ])


def test_report_empty(reportjudge, report):
    # dummy report (always passes)
    rpt = report()
    (punishment, rules_broken) = reportjudge.make_judgement(rpt)
    assert len(rules_broken) == 0
    assert punishment == None

def test_report_rule1(reportjudge, report):
    # bad username (silence)
    rpt = report(
        reported={
            "username": "evilusername",
            "account": {
                "username": "evilusername"
            }
        }
    )
    (punishment, rules_broken) = reportjudge.make_judgement(rpt)
    assert len(rules_broken) == 1
    for first_item in rules_broken:
        assert first_item.name == "Rule 1"
        assert isinstance(first_item, UsernameContentRule)
    assert punishment.type == "silence"

def test_report_rule2(reportjudge, report):
    # bad message (suspend)
    rpt = report(
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
    (punishment, rules_broken) = reportjudge.make_judgement(rpt)
    assert len(rules_broken) == 1
    for first_item in rules_broken:
        assert first_item.name == "Rule 2"
        assert isinstance(first_item, MessageContentRule)
    assert punishment.type == "suspend"

def test_report_multirule(reportjudge, report):
    # multiple rule breaks (highest severity takes precendence)
    rpt = report(
        reported={
            "username": "evilusername",
            "account": {
                "username": "evilusername"
            }
        },
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
    (punishment, rules_broken) = reportjudge.make_judgement(rpt)
    assert len(rules_broken) == 2
    for rule in rules_broken:
        assert rule.name in ["Rule 1", "Rule 2"]
        assert isinstance(rule, (MessageContentRule, UsernameContentRule))
    assert punishment.type == "suspend"

def test_pending_empty(pendingjudge, pending_account):
    # dummy pending account (always passes)
    acct = pending_account()
    (punishment, rules_broken) = pendingjudge.make_judgement(acct)
    assert len(rules_broken) == 0
    assert punishment == None

def test_pending_rule1(pendingjudge, pending_account):
    # bad username (silence)
    acct = pending_account(username="evilusername")
    (punishment, rules_broken) = pendingjudge.make_judgement(acct)
    assert len(rules_broken) == 1
    for first_item in rules_broken:
        assert first_item.name == "Rule 1"
        assert isinstance(first_item, UsernameContentRule)
    assert punishment.type == "silence"

def test_pending_rule2(pendingjudge, pending_account):
    # bad message (suspend)
    acct = pending_account(message="<p>this post contains a badword ban me pls</p>")
    (punishment, rules_broken) = pendingjudge.make_judgement(acct)
    assert len(rules_broken) == 1
    for first_item in rules_broken:
        assert first_item.name == "Rule 2"
        assert isinstance(first_item, MessageContentRule)
    assert punishment.type == "suspend"

def test_pending_multirule(pendingjudge, pending_account):
    # multiple rule breaks (highest severity takes precendence)
    acct = pending_account(
        username="evilusername",
        message="<p>this post contains a badword ban me pls</p>"
    )
    (punishment, rules_broken) = pendingjudge.make_judgement(acct)
    assert len(rules_broken) == 2
    for rule in rules_broken:
        assert rule.name in ["Rule 1", "Rule 2"]
        assert isinstance(rule, (MessageContentRule, UsernameContentRule))
    assert punishment.type == "suspend"
