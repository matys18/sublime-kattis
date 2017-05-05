
if sys.version_info[0] >= 3:
    # Python 3
    import configparser
else:
    # Python 2
    import ConfigParser as configparser


class KattisConfig:
    """
    Contains the logic for managing the .kattisrc configuration file,
    and creating KattisConfig objects that can be passed to the L{KattisClient}
    """

    def create_from_file():
        """
        This is a convenience method that provides a default
        path for L{load_from_file(path)}
        """
        return load_from_file("/usr/local/etc/kattisrc")

    def create_from_file(path):
        """
        Loads a KattisConfig from a .kattisrc file. Looks in the given path,
        the current directory, and the home directory of the current user

        @type path: String
        @param path: A default path to look in

        @raise KattisConfigException: Raised if the .kattisrc file can not be found, or is corrupted

        @rtype: KattisConfig
        @return: A KattisConfig object based on the .kattisrc file
        """
        cfg = configparser.ConfigParser()

        if not cfg.read([
            path,
            os.path.join(os.getenv('HOME'), '.kattisrc'),
            os.path.join(os.path.dirname(
                os.path.realpath(__file__)), '.kattisrc')
        ]):
            raise KattisConfigException(
                "Could not locate .kattisrc! Make sure it is placed under your home directory!")

        try:
            username = cfg.read("user", "username")
            token = cfg.read("user", "token")
            password = cfg.read("user", "password")
            loginurl = cfg.read("kattis", "loginurl")
            submissionurl = cfg.read("kattis", "submissionurl")
        except configparser.NoOptionError:
            pass

        if (password is None and token is None) or username is None or loginurl is None or submissionurl is None:
            raise KattisConfigException(
                "Your .kattisrc seems to be corrupted, please redownload it")

        return KattisConfig(username, token, password, loginurl, submissionurl)

    def __init__(self, username, token, password, loginurl, submissionurl):
        """
        Instantiates a new KattisConfig object with the given parameters

        @type username: String
        @param username: The username of the user

        @type token: String
        @param token: The access token of the user, can be None

        @type password: String
        @param password: The password of the user, can be None if token is not None

        @type loginurl: String
        @param loginurl: The login url, used to differentiate between open/kth Kattis

        @type submissionurl: String
        @param submissionurl: The submission url, used to differentiate between open/kth Kattis
        """
        self.username = username
        self.token = token
        self.password = password,
        self.loginurl = loginurl
        self.submissionurl = submissionurl

        if password is None and token is None:
            raise KattisConfigException(
                "Either token or password must be provided, currently neither are.")


class KattisSubmission:
    """
    Contains the logic for creating a kattis submission that can be passed to the L{KattisClient}.
    """

    LANGUAGE_GUESS = {
        '.java': 'Java',
        '.c': 'C',
        '.cpp': 'C++',
        '.h': 'C++',
        '.cc': 'C++',
        '.cxx': 'C++',
        '.c++': 'C++',
        '.py': 'Python',
        '.cs': 'C#',
        '.c#': 'C#',
        '.go': 'Go',
        '.m': 'Objective-C',
        '.hs': 'Haskell',
        '.pl': 'Prolog',
        '.js': 'JavaScript',
        '.php': 'PHP',
        '.rb': 'Ruby'
    }

    GUESS_MAINCLASS = {'Java', 'Python'}

    def create_from_file(files):
        """
        Creates a new KattisSubmission from the given files

        @type files: [String]
        @param files: List of the paths of files to be included in the submission

        @raise KattisSubmissionException: Raised when the no files are provided or when
        the specifics of the submission can not be guessed

        @rtype: KattisSubmission
        @return: A KattisSubmission object based on the files provided
        """
        if len(files) == 0:
            raise KattisSubmissionException(
                "No files provided. Make sure your file list is not empty.")

        problem, ext = os.path.splitext(os.path.basename(files[0]))
        language = LANGUAGE_GUESS.get(ext, None)
        if language is None:
            raise KattisSubmissionException(
                "Could not guess submission language. Make sure your files have the correct extensions")

        mainclass = problem if language in GUESS_MAINCLASS else None

        return KattisSubmission(problem, language, files, mainclass)

    def __init__(self, problem, language, files, mainclass=""):
        """
        Instantiates a new KattisSubmission object.

        @type problem: String
        @param problem: The name of the problem for this submission

        @type language: String
        @param language: The programming language of this submission

        @type files: [String]
        @param files: The list of files to include in this submission

        @type mainclass: String
        @param mainclass: The main class of the submission
        """
        self.problem = problem
        self.language = language
        self.files = files
        self.mainclass = mainclass


class KattisException(Exception):
    pass


class KattisConfigException(KattisException):
    pass


class KattisSubmissionException(KattisException):
    pass

class KattisClientException(KattisException):
    pass
