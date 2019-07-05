# Ivory, a crappy Mastodon automoderator

Ivory is an automoderation system for Mastodon which logs in as a normal user to
the Mastodon frontend, scans the reports page, and automatically deals with
common moderation tasks, particularly spam. It does this by reading over each
report it finds and running a number of configuration-declared *rules* which are
checked on each report.

Currently, Ivory is intended to function as a stopgap measure to curb spam while
we await the actual moderation API, though I have intentionally designed things
in a way that will allow me to convert it to use said API when (or if) it
releases.

## Installation and Usage

First, install Geckodriver and make sure it's in your terminal's PATH. If you're
running Linux, you may have a version in your distro's package manager.

After doing that, snippet should work. You'll want Python 3 (preferably 3.7 or
above) for this:

```bash
git clone https://github.com/bclindner/ivory
cd ivory
python -m venv .
source bin/activate
pip install -r requirements.txt
```

After that, create a config.yml in the project root as shown in the Configuring
section below and then run:

```bash
python .
```

You will be asked for a username and password, and optionally an OTP if your
account is set up for that. This should only happen once; after that, cookies
are stored in the project root as `cookies.pickle` and the app will log in with
those. (If at some point Ivory stops signing in correctly, delete this file and
try manually logging in again.)

## Configuring

Ivory is configured using a YAML file. An example configuration is below:
```yaml
# Time to wait in between checks (in seconds)
wait_time: 600 # 10min; lower numbers shouldn't stress your servers out
driver:
  type: browser # browser is the only supported driver type at present
  # Instance URL
  instance_url: https://mastodon.technology
# Array of rules for Ivory to judge with
rules:
  # This name is what Ivory mentions in the moderation notes when finishing a
  # report.
- name: "No womenarestupid.site spam links"
  # This rule parses over links in every post attached to a report.
  # Also supports text phrases in reported posts with the 'content' type.
  type: link_content
  blocked:
  # This list supports regexes!
  - womenarestupid.site
  - dontmarry.com
  punishment:
    # The highest severity punishment in a single judgement is the one used when
    # punishing the user.
    severity: 1000
    # Currently only suspend is supported.
    type: suspend
    # Not implemented, but the following are for local users.
    delete_account_data: yes
    local_suspend_message: "Your account has been suspended for spamming."
- name: "No womenarestupid.site shorturls"
  # This rule type resolves shorturls!
  type: link_resolver
  blocked:
  - dontmarry.com
  - womenarestupid.site
  punishment:
    severity: 1000
    type: suspend
    delete_account_data: yes
    local_suspend_message: "Your account has been suspended for spamming."
- name: "No inflammatory usernames"
  type: username_content
  blocked:
  # You can do case insensitive searches using regex, too!
  - (?i)heck
  punishment:
    severity: 1000
    type: suspend
    delete_account_data: yes
    local_suspend_message: "Your account has been suspended for having an inflammatory username."
```

## Caveats

This code is using Selenium to drive its report handling system. Selenium can be
finicky. Stuff can break.

Take care when writing your rules. Ivory doesn't care if you get them wrong, and
Ivory will absolutely ban users with impunity if you do. Test them if you can.
Support for dry runs will come available when I get to it.

## Maintainers

This is currently solely maintained by me,
[@bclindner@mastodon.technology](http://mastodon.technology/@bclindner).


## Bugs & Contributing

Contributions welcome. I'm a JS dev, not a Python one, so I may well need
them.

Got bugs or feature request? File them as a GitHub issue and I'll address them
when I can. Same goes for PRs.
