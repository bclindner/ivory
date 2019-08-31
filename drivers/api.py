from core import Driver, Report, Punishment
from mastodon import Mastodon, MastodonNetworkError
from exceptions import ConfigurationError, DriverError, DriverAuthorizationError, DriverNetworkError, PunishmentNotImplementedError


class MastodonAPIDriver(Driver):
    """
    Driver which directly handles reports using the Mastodon API.

    Requires Mastodon 2.9.1+. (This is checked at runtime.)
    """
    supported_punishments = ['disable', 'silence', 'suspend']

    def __init__(self, config):
        Driver.__init__(self, config)
        try:
            self.__api = Mastodon(
                api_base_url=config['instance_url'],
                client_id=config['client_id'],
                client_secret=config['client_secret']
            )
        except KeyError as err:
            key = err.args[0]
            raise ConfigurationError(key + " not found")
        except MastodonNetworkError:
            raise DriverNetworkError(
                "failed to get instance version is instance_url valid?")
        if self.__api.verify_minimum_version("2.9.1") is False:
            raise DriverError(
                "server does not appear to support Moderation API - expected version 2.9.1+")

    def get_reports(self, since_id: int):
        report_dicts = self.__api.admin_reports(since_id=since_id)
        reports = []
        for report_dict in report_dicts:
            pass
            # TODO unmarshal report into Report object
            # reports.append(Report.fromdict(report_dict))

    def punish(self, report: Report, punishment: Punishment):
        if punishment.type in ['suspend', 'silence', 'disable']:
            self.__api.admin_account_moderate(
                report.reported.user_id,
                action=punishment.type,
                report=report.report_id)
        else:
            raise PunishmentNotImplementedError(punishment.type)

    def add_note(self, report: Report, message: str, resolve: bool = False):
        # NOT IMPLEMENTED IN API ITSELF; log to console for now
        print("Note on report", str(report.report_id)+":", message)
        if resolve:
            self.__api.admin_report_resolve(report.report_id)
        pass
