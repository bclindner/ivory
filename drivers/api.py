from core import Driver
from mastodon import Mastodon, MastodonNetworkError
from exceptions import ConfigurationError, DriverError, DriverAuthorizationError, DriverNetworkError

class MastodonAPIDriver(Driver):
    """
    Driver which directly handles reports using the Mastodon API.
    
    Requires Mastodon 2.9.1+. (This is checked at runtime.)
    """
    def __init__(self, config):
        Driver.__init__(self, config)
        try:
            self.__api = Mastodon(
                api_base_url = config['instance_url'],
                client_id = config['client_id'],
                client_secret = config['client_secret']
            )
        except KeyError as err:
            key = err.args[0]
            raise ConfigurationError(key + " not found")
        except MastodonNetworkError:
            raise DriverNetworkError("failed to get instance version is instance_url valid?")
        if self.__api.verify_minimum_version("2.9.1") == False:
            raise DriverError("server does not appear to support Moderation API - expected version 2.9.1+")