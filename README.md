# Ivory, a crappy Mastodon automoderator

Ivory is an automoderation system for Mastodon which logs in as a normal user to
the Mastodon frontend, scans the reports page, and automatically deals with
common moderation tasks, particularly spam. It does this by reading over each
report it finds and running a number of configuration-declared *rules* which are
checked on each report.

## Configuring

Ivory is configured using a YAML file. An example configuration is below:
```yaml
instance_url: https://mastodon.technology
rules:
- name: "No womenarestupid.site spam"
  type: link
  blocked:
  - womenarestupid.site
  punishment:
    severity: 1000
    type: suspend
    delete_account_data: yes
    local_suspend_message: "Your account has been suspended for spamming."
```

## Caveats

This code is using Selenium to drive its report handling system. Selenium can be
finicky. Stuff can break.

## Maintainers

This is currently solely maintained by me,
[@bclindner@mastodon.technology](http://mastodon.technology/@bclindner).

Contributions welcome. I'm a JS dev, not a Python one, so I may well need
them.
