from voluptuous import Schema, Required, Any, Url, ALLOW_EXTRA
import constants

Punishment = Schema({
    Required("type"): Any(
        constants.PUNISH_WARN,
        constants.PUNISH_REJECT,
        constants.PUNISH_DISABLE,
        constants.PUNISH_SILENCE,
        constants.PUNISH_SUSPEND
    )
}, extra=ALLOW_EXTRA)

Rule = Schema({
    Required("name"): str,
    Required("type"): str,
    Required("severity"): int,
    Required("punishment"): Punishment,
}, extra=ALLOW_EXTRA)

Reports = Schema({
    Required("rules"): [Rule]
})

PendingAccounts = Schema({
    Required("rules"): [Rule]
})

IvoryConfig = Schema({
    Required("token"): str,
    # I know I should be using Url() here but it didn't work and I'm tired
    Required("instanceURL"): str,
    "waitTime": int,
    "dryRun": bool,
    "logLevel": Any("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
    "reports": Reports,
    "pendingAccounts": PendingAccounts
})

# Schemas used by several rules

RegexBlockingRule = Rule.extend({
    Required("blocked"): [str]
})

