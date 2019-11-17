# Ivory

Ivory is an automoderator and anti-spam tool for Mastodon admins. It automates
handling certain trivial reports and new user requests using *rules* -
configurable tests for reports that check for bad words, malicious links, and
more.

## Installation Guide

This installation guide assumes you know your way around a Linux terminal and
know a little bit about common tech like Python and the `venv` package, and JSON
formatting.

### Installing

In a Linux terminal, the following command will clone and install Ivory to
whichever folder you're in:

```bash
git clone https://github.com/bclindner/ivory
cd ivory
python -m venv .
source bin/activate
python -m pip install -r requirements.txt
```

### Configuration

Before starting Ivory, you need to create a new application in the Mastodon
frontend's settings. Don't worry about setting redirect URIs or anything that
isn't required - just make sure you enable all of the admin: scopes. 

*Be* ***EXTREMELY*** *careful with the access token this generates - this key
has a lot of power and in the wrong hands, this access key could mean someone
completely obliterating your instance.*

Once you've done that, it's time to set up your config file. Configuring Ivory
is done with JSON; a sample is below:

```json
{
  "token": "<YOUR_ACCESS_TOKEN_HERE>",
  "instanceURL": "<YOUR_INSTANCE_URL_HERE",
  "waitTime": 300,
  "reports": {
    "rules": [
      {
        "name": "No spam links",
        "type": "link_resolver",
        "blocked": ["evilspam\\.website", "dontmarry\\.com"],
        "severity": 1,
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
          "type": "suspend",
          "message": "Your account has been suspended for spamming."
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

A full list of rules can be found on the [wiki](#).

Ideally you only have to change this once in a blue moon, but if you do, you can
use the `"dryRun": true` option to prevent Ivory from actually taking action.

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
applying your set rules.

## Extending

You'll notice the `rules/` folder is a flat folder of Python scripts, one per
Ivory rule. You can easily create your own rules by just dropping in a new
Python file and writing one similar to the others in the folder.

## Bugs & Contributing

If you have any issues with Ivory not working as expected, please file a GitHub
issue.

Contributions are also welcome - send in pull requests if you have anything new
to add.

If you have any other questions, go ahead and [ping me on
Mastodon](https://mastodon.technology/@bclindner) and I might be able to answer
them.
