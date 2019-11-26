# Ivory

Ivory is an automoderator and anti-spam tool for Mastodon admins. It automates
handling certain trivial reports and new user requests using *rules* -
configurable tests that check reports and pending users for bad usernames,
malicious links, and more.

## Installation Guide

This installation guide assumes you know your way around a Linux terminal,
have Python and Git installed, and maybe a little bit about common tech like
Python and JSON formatting.

### Installing


In a Linux terminal, the following commands will clone and install Ivory to
whichever folder you're in. Make sure you have Git and Python installed:

```bash
git clone https://github.com/bclindner/ivory
cd ivory
python -m venv .
source bin/activate
python -m pip install -r requirements.txt
```

This repo also comes with a Dockerfile, so if you want to deploy with that, that
works too:

```bash
git clone https://github.com/bclindner/ivory
cd ivory
docker build -t ivory .
docker run -v /srv/ivory/ivory_config.json:/app/config.json ivory
```

### Configuration

Before starting Ivory, you need to create a new application in the Preferences
menu. Don't worry about setting redirect URIs or anything that isn't required -
just make sure you enable all of the `admin:` scopes. Once you've created the
application, you'll want to grab its access token to place in the configuration
file (example below).

*Be* ***EXTREMELY*** *careful with handling the access token this generates -
this key has a lot of power and in the wrong hands, this could mean someone
completely obliterating your instance.*

Once you've done that, it's time to set up your config file. Configuring Ivory
is done with JSON; a sample is below:

```json
{
  "token": "<YOUR_ACCESS_TOKEN_HERE>",
  "instanceURL": "<YOUR_INSTANCE_URL_HERE>",
  "waitTime": 300,
  "reports": {
    "rules": [
      {
        "name": "No spam links",
        "type": "link_resolver",
        "blocked": ["evilspam\\.website", "dontmarry\\.com"],
        "severity": 2,
        "punishment": {
          "type": "suspend",
          "message": "Your account has been suspended for spamming."
        }
      },
      {
        "name": "No link-in-bio spammers",
        "type": "bio_content",
        "blocked": ["sexie.ru"],
        "severity": 1,
        "punishment": {
          "type": "disable",
          "message": "Your account has been disabled for spamming."
        }
      }
    ]
  },
  "pendingAccounts": {
    "rules": [
      {
        "name": "No <a> tags",
        "_comment": "Because honestly, you're definitely a bot if you're putting <a> tags into the field",
        "type": "message_content",
        "blocked": ["<a href=\".*\">.*</a>"],
        "severity": 1,
        "punishment": {
          "type": "reject"
        }
      },
      {
        "name": "StopForumSpam test",
        "type": "stopforumspam",
        "threshold": 95,
        "severity": 1,
        "punishment": {
          "type": "reject"
        }
      }
    ]
  }
}
```

A more [in-depth guide to Ivory configuration](https://github.com/bclindner/ivory/wiki/Getting-Started)
and the list of [rules](https://github.com/bclindner/ivory/wiki/Rules) and
[punishments](https://github.com/bclindner/ivory/wiki/Punishments)
can be found on the wiki.

Ideally you only have to change this once in a blue moon, but if you do, you can
use the `"dryRun": true` option to prevent Ivory from taking action, so you can
test some rules on recent live moderation queues.

### Running

After you've set up a config file, run the following in a Linux terminal:

```
# if you're running in the same terminal session you installed from, you can
# skip this next line:
source bin/activate
python .
```

Hopefully, no errors will be thrown and Ivory will start up and begin its first
moderation pass, reading the first page of active reports and pending users and
applying your set rules. Ivory will handle these queues every 300 seconds,
or 5 minutes. (This is controlled by the `waitTime` part of the above config
file - if you wanted 10 minutes, you could set it to 600!)

If you'd rather run it on some other schedule via a proper task scheduler like
cron or a systemd .timer unit, you can use `python . oneshot` which will run
Ivory only once. This sample cron line will run Ivory every 5 minutes and output
to a log file:

```cron
*/5 * * * * cd /absolute/path/to/ivory; ./bin/python . oneshot >> ivory.log
```

## Extending (custom rules)

You'll notice the `rules/` folder is a flat folder of Python scripts, one per
Ivory rule. If you've got a little Python experience, you can easily create your
own rules by just dropping in a new Python file and using one of the other files
in the folder as a jumping-off point.

The reports and pending accounts that Ivory rules receive are the same as what
Mastodon.py provides for
[reports](https://mastodonpy.readthedocs.io/en/stable/#report-dicts) and [admin
accounts](https://mastodonpy.readthedocs.io/en/stable/#admin-account-dicts),
respectively.

**Don't forget to use `dryRun` in your config when testing your new rule!**

Once you've finished writing up your custom rule, say as
`rules/filename_of_your_rule.py`, you can address it by its filename in your
config:

```json
...
"pendingAccounts": {
  "rules": [
    {
      "name": "An instance of my cool new rule",
      "type": "filename_of_your_rule",
      "custom_option": true,
      "severity": 5,
      "punishment": {
        "type": "reject"
      }
    },
  ]
}
...
```

If you come up with any useful rules and wouldn't mind writing a schema and some
tests for it, making a pull request to include it in Ivory's main release would
be highly appreciated! The more rules Ivory gets, the more tools are
collectively available to other admins for dealing with spammers and other
threats to the Fediverse at large.

## Bugs & Contributing

If you have any issues with Ivory not working as expected, please file a GitHub
issue.

Contributions are also welcome - send in pull requests if you have anything new
to add.

If you have any other questions, go ahead and [ping me on
Mastodon](https://mastodon.technology/@bclindner) and I might be able to answer
them.
