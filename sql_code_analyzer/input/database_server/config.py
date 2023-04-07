import configparser
import inspect

from sql_code_analyzer.output.reporter.base import ProgramReporter


class DBConfig:
    """
    Encapsulate the entered login details to object.
    """

    def __init__(self, path: str, option: str):

        self.config = configparser.ConfigParser()
        self.config.read(path)

        self.option = option

        self.dialect = self.config.get(self._option, "dialect", fallback=None)
        self.username = self.config.get(self._option, "username", fallback=None)
        self.password = self.config.get(self._option, "password", fallback=None)
        self.host = self.config.get(self._option, "host", fallback=None)
        self.port = self.config.get(self._option, "port", fallback=None)
        self.service = self.config.get(self._option, "service", fallback=None)

        self.validate_args_presence()

    @property
    def option(self):
        return self._option

    @option.setter
    def option(self, value):
        value = value.split(' #')[0].lstrip().rstrip()
        if value.startswith("#"):
            value = None

        self._option = value

    @property
    def dialect(self):
        return self._dialect

    @dialect.setter
    def dialect(self, value):
        value = value.split(' #')[0].lstrip().rstrip()
        if value.startswith("#"):
            value = None

        self._dialect = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        value = value.split(' #')[0].lstrip().rstrip()
        if value.startswith("#"):
            value = None

        self._username = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        value = value.split(' #')[0].lstrip().rstrip()
        if value.startswith("#"):
            value = None

        self._password = value

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        value = value.split(' #')[0].lstrip().rstrip()
        if value.startswith("#"):
            value = None

        self._host = value

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        value = value.split(' #')[0].lstrip().rstrip()
        if value.startswith("#"):
            value = None

        self._port = value

    @property
    def service(self):
        return self._service

    @service.setter
    def service(self, value):
        value = value.split(' #')[0].lstrip().rstrip()
        if value.startswith("#"):
            value = None

        self._service = value

    def validate_args_presence(self):
        """
        Verify if all necessary login data are set.

        :return:
        """

        def is_property(item):
            return isinstance(item, property)

        properties_if_none = [name for name, value in inspect.getmembers(DBConfig, is_property)
                              if getattr(self, name) is None]

        if len(properties_if_none):
            ProgramReporter.show_error_message(
                message="Parameter(s) " + " ".join(str(item) for item in properties_if_none) + " are not set!."
            )

