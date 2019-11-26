import pytest
import ivory
import time

ivoryconfig = {
  "token": "testtoken",
  "instanceURL": "https://testinstance.local",
  "waitTime": 300,
  "logLevel": "DEBUG",
  "reports": {
    "rules": [
      {
        "name": "No bad usernames",
        "type": "username_content",
        "blocked": ["badword"],
        "severity": 1,
        "punishment": {
          "type": "suspend",
          "message": "Your account has been suspended for spamming."
        }
      },
      {
        "name": "No badwords",
        "type": "message_content",
        "blocked": ["badword"],
        "severity": 1,
        "punishment": {
          "type": "disable",
          "message": "Your account has been disabled for having a badword in a message."
        }
      }
    ]
  },
  "pendingAccounts": {
    "rules": [
      {
        "name": "No probbox spammers",
        "type": "message_content",
        "blocked": ["badword", "slur[^p]"],
        "severity": 1,
        "punishment": {
          "type": "reject"
        }
      },
      {
        "name": "No mewkid spammers",
        "type": "username_content",
        "blocked": ["badword", "slur[^p]"],
        "severity": 1,
        "punishment": {
          "type": "reject"
        }
      }
    ]
  }
}

@pytest.fixture
def generate_mockstodon(monkeypatch):
    """
    Replace Mastodon.py completely with a custom copy that replicates the functions Ivory uses.

    I hate having to do this but I don't know if there's really a better way to
    test without doing this...
    """
    def _generate_mockstodon(**kwargs):
        class Mockstodon():
            # Static values we check in the tests
            # these are 4-tuples in the form of:
            # (account id, action, report id, message)
            moderation_actions = []
            accounts = []
            reports = []
            def __init__(self, **kwargs):
                # We don't actually use these values internally, we just want to make sure Mastodon.py is getting passed the right stuff
                assert kwargs.get("access_token") == ivoryconfig['token']
                assert kwargs.get("api_base_url") == ivoryconfig['instanceURL']
            def verify_minimum_version(self, version):
                return True
            def instance(self):
                return {
                    "uri": ivoryconfig['instanceURL'],
                }
            def account_verify_credentials(self):
                return {
                    "username": "testuser"
                }
            def admin_reports(self):
                return self.reports
            def admin_accounts(self, **kwargs):
                if kwargs.get("status") == "pending":
                    return self.accounts
                else:
                    assert kwargs.get("status") == "pending"
            def admin_account_reject(self, acct_id):
                self.moderation_actions.append((acct_id, "reject", None, None))
                return
            def admin_account_moderate(self, acct_id, action, report_id, **kwargs):
                self.moderation_actions.append((acct_id,action,report_id, kwargs.get("message")))
                return
        Mockstodon.accounts = kwargs.get("accounts")
        Mockstodon.reports = kwargs.get("reports")
        monkeypatch.setattr(ivory, "Mastodon", Mockstodon)
        return Mockstodon
    return _generate_mockstodon

def test_oneshot(generate_mockstodon, report, pending_account):
    """
    Verify that Ivory runs.
    """
    Mockstodon = generate_mockstodon(reports=[
        # suspend
        report(reported={
            "username": "badword",
            "account": {
                "username": "badword"
            }
        }),
        # disable
        report(statuses=[
            {
                "content": "badword"
            }
        ]),
        # clean
        report()
    ], accounts=[
        # clean
        pending_account(),
        # reject
        pending_account(username="badword"),
        # reject
        pending_account(message="badword")
    ])
    i = ivory.Ivory(ivoryconfig)
    i.run()
    assert Mockstodon.moderation_actions == [
        ('1', 'suspend', '1', None),
        ('1', 'disable', '1', None),
        ('1', 'reject', None, None),
        ('1', 'reject', None, None)
    ]
