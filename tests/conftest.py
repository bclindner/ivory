import pytest
import requests

@pytest.fixture(autouse=True)
def disable_requests(monkeypatch):
    """
    Prevent Requests from making any actual network requests.
    (This also prevents Mastodon.py from doing anything, as it uses requests as
    well.)
    """
    monkeypatch.delattr("requests.sessions.Session.request")

@pytest.fixture
def MockResponse():
    """
    Returns an extendable class that resembles the Requests response class.
    """
    class _MockResponse:
        def __init__(self, **kwargs):
            self.jsonresponse = kwargs.get("json")
            self.url = kwargs.get("url")
        def json(self):
            return self.jsonresponse
    return _MockResponse

@pytest.fixture
def account_field():
    def _account_field(**kwargs):
        field = {
            "name": kwargs.get("name", "name"),
            "value": kwargs.get("value", "value"),
        }
        if kwargs.get('verified') is True:
            field["verified_at"] = "2019-01-01T00:00:00.000Z"
        return field
    return _account_field


@pytest.fixture
def account(account_field):
    def _account(**kwargs):
        fields = []
        for cfg in kwargs.get("fields", []):
            fields.append(account_field(**cfg))
        return {
            "id": kwargs.get("account_id", "1"),
            "username": kwargs.get("username", "fakeuser"),
            "acct": kwargs.get("username", "fakeuser"),
            "display_name": kwargs.get("username", "fakeuser"),
            "locked": False,
            "bot": False,
            "created_at": "2019-01-01T00:00:00.000Z",
            "note": kwargs.get("note", ""),
            "url": "https://example.com/@user",
            "avatar": "https://cdn.example.com/testavatar.png",
            "avatar_static": "https://cdn.example.com/testheader.png",
            "header": "https://cdn.example.com/testheader.png",
            "header_static": "https://cdn.example.com/testheader.png",
            "followers_count": 100,
            "following_count": 100,
            "statuses_count": 100,
            "last_status_at": "2019-01-01T00:00:00.000Z",
            "emojis": [],
            "fields": fields
        }
    return _account


@pytest.fixture
def pending_account(account):
    def _pending_account(**kwargs):
        return {
            "id": kwargs.get("account_id", "1"),
            "username": kwargs.get("username", "fakeuser"),
            "domain": None,
            "created_at": "2019-01-01T00:00:00.000Z",
            "email": kwargs.get("email", "testuser@example.com"),
            "ip": kwargs.get("ip", "127.0.0.1"),
            "role": "user",
            "confirmed": True,
            "suspended": False,
            "silenced": False,
            "disabled": False,
            "approved": False,
            "locale": "en",
            "invite_request": kwargs.get("message", "Test message."),
            "account": account(**kwargs.get("account", {}))
        }
    return _pending_account

@pytest.fixture
def pending_account_no_invite(account):
    def _pending_account_no_invite(**kwargs):
        return {
            "id": kwargs.get("account_id", "1"),
            "username": kwargs.get("username", "fakeuser"),
            "domain": None,
            "created_at": "2019-01-01T00:00:00.000Z",
            "email": kwargs.get("email", "testuser@example.com"),
            "ip": kwargs.get("ip", "127.0.0.1"),
            "role": "user",
            "confirmed": True,
            "suspended": False,
            "silenced": False,
            "disabled": False,
            "approved": False,
            "locale": "en",
            "invite_request": None,
            "account": account(**kwargs.get("account", {}))
        }
    return _pending_account_no_invite


@pytest.fixture
def admin_account(account):
    def _admin_account(**kwargs):
        return {
            "id": kwargs.get("account_id", "1"),
            "username": kwargs.get("username", "fakeuser"),
            "domain": kwargs.get("domain"),
            "created_at": "2019-01-01T00:00:00.000Z",
            "email": kwargs.get("email", "testuser@example.com"),
            "ip": kwargs.get("ip", "127.0.0.1"),
            "role": "user",
            "confirmed": True,
            "suspended": False,
            "silenced": False,
            "disabled": False,
            "approved": True,
            "locale": "en",
            "invite_request": None,
            "account": account(**kwargs.get("account", {}))
        }
    return _admin_account


@pytest.fixture
def report(account, admin_account, status):
    def _report(**kwargs):
        reporter = admin_account(**kwargs.get("reporter", {}))
        reported = admin_account(**kwargs.get("reported", {}))
        statuses = []
        for cfg in kwargs.get("statuses", []):
            statuses.append(status(**cfg))
        return {
            "id": kwargs.get("report_id", "1"),
            "action_taken": False,
            "comment": kwargs.get("comment", ""),
            "created_at": "2019-01-01T00:00:00.000Z",
            "updated_at": "2019-01-01T00:00:00.000Z",
            "account": reporter,
            "target_account": reported,
            "assigned_account": None,
            "action_taken_by_account": None,
            "statuses": statuses
        }
    return _report

@pytest.fixture
def status_tag():
    def _status_tag(name):
        return {
            "name": name,
            "url": "https://example.com/tags/{}".format(name)
        }
    return _status_tag

@pytest.fixture
def status(account, status_tag):
    def _status(**kwargs):
        tags = []
        for tagname in kwargs.get("tags", []):
            tags.append(status_tag(tagname))
        return {
            "id": kwargs.get("status_id", "1"),
            "created_at": "2019-01-01T00:00:00.000Z",
            "in_reply_to_id": kwargs.get("reply_id", "1"),
            "in_reply_to_account_id": kwargs.get("replying_to_id", "1"),
            "sensitive": bool(kwargs.get("spoiler_text", None)),
            "spoiler_text": kwargs.get("spoiler_text", None),
            "visibility": "public",
            "language": "en",
            "uri": "https://example.com/users/testuser/statuses/1",
            "url": "https://example.com/@testuser/1",
            "replies_count": 1,
            "reblogs_count": 0,
            "favourites_count": 0,
            "favourited": False,
            "reblogged": False,
            "muted": False,
            "content": kwargs.get("content", "<p>Test post.</p>"),
            "reblog": None,
            "account": account(**kwargs.get("author", {})),
            "media_attachments": [],
            "mentions": [
                {
                    "id": "1",
                    "username": "fakeuser",
                    "url": "https://example.com/@testuser",
                    "acct": "fakeuser@example.com"
                }
            ],
            "tags": [{"name": "hashtag", "url": "https://example.com/tags/hashtag"}],
            "emojis": [],
            "card": None,
            "poll": None
        }
    return _status
