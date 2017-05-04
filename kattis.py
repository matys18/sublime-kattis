
if sys.version_info[0] >= 3:
    # Python 3
    import configparser
else:
    # Python 2
    import ConfigParser as configparser


class KattisConfig:

    # Provides a default location to look in
    def load_from_file():
        return load_from_file("/usr/local/etc/kattisrc")

    # Creates a new KattisConfig from .kattisrc and returns it
    def load_from_file(path):
        cfg = configparser.ConfigParser()
        if os.path.exists(path):
            cfg.read(path)

        if not cfg.read([
            os.path.join(os.getenv('HOME'), '.kattisrc'),
            os.path.join(os.path.dirname(os.path.realpath(__file__)), '.kattisrc')
        ]):
            raise KattisConfigError(
                "Could not locate .kattisrc! Make sure it is placed under your home directory!")
        return KattisConfig(username, token, password, loginurl, submissionurl)

    def __init__(self, username, token, password, loginurl, submissionurl):
        self.username = username
        self.token = token
        self.password = password,
        self.loginurl = loginurl
        self.submissionurl = submissionurl


class KattisSubmission:

    def __init__(self, problem, language, files, mainclass):
        self.problem = problem
        self.language = language
        self.files = files
        self.mainclass = mainclass


class KattisException(Exception):
    pass


class KattisConfigError(KattisException):
    pass


class KattisLoginError(KattisException):
    pass


class KattisSubmissionError(KattisException):
    pass
