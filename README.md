# Ivory, a crappy Mastodon automoderator

Ivory is an automoderation system for Mastodon which logs in as a normal user
to the Mastodon frontend, scan the reports page, and automatically deal with
common moderation tasks, particularly spam. It does this by reading over each
report it finds and running a number of configuration-declared *rules* to 

## Configuring

Ivory is configured using a YAML file. An example configuration showcasing all
available moderation rules is below:
```yaml
```

## Caveats

This code is using Selenium to drive its report handling system. Selenium can be
finicky. Stuff can break.

## Maintainers

This is currently solely maintained by me,
[@bclindner@mastodon.technology](http://mastodon.technology/@bclindner).

Contributions welcome. I'm a JS dev, not a Python one, so I may well need
them.
