"""
Config schemas used in Ivory and its rules.
"""
from voluptuous import Schema, Required, Any, Url, ALLOW_EXTRA
import constants

ReportPunishment = Schema({
    Required("type"): Any(
        constants.PUNISH_WARN,
        constants.PUNISH_REJECT,
        constants.PUNISH_DISABLE,
        constants.PUNISH_SILENCE,
        constants.PUNISH_SUSPEND
    )
}, extra=ALLOW_EXTRA)

PendingAcctPunishment = Schema({
    Required("type"): Any(
        constants.PUNISH_REJECT
    )
}, extra=ALLOW_EXTRA)

Rule = Schema({
    Required("name"): str,
    Required("type"): str,
    Required("severity"): int,
}, extra=ALLOW_EXTRA)

ReportRule = Rule.extend({
    Required("punishment"): ReportPunishment
})

PendingAcctRule = Rule.extend({
    Required("punishment"): PendingAcctPunishment
})

Reports = Schema({
    Required("rules"): [ReportRule]
})

PendingAccounts = Schema({
    Required("rules"): [PendingAcctRule]
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

