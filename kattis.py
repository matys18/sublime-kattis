import sys
import os
import requests

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

    @staticmethod
    def create_from_file(path="/usr/local/etc/kattisrc"):
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

        username = token = password = loginurl = submissionurl = None

        try:
            username = cfg.get("user", "username")
        except configparser.NoOptionError:
            pass

        try:
            token = cfg.get("user", "token")
        except configparser.NoOptionError:
            pass

        try:
            password = cfg.get("user", "password")
        except configparser.NoOptionError:
            pass

        try:
            loginurl = cfg.get("kattis", "loginurl")
        except configparser.NoOptionError:
            pass

        try:
            submissionurl = cfg.get("kattis", "submissionurl")
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
        '.py': 'Python 3',
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

    @staticmethod
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
                "No files provided. Make sure your file list is not empty")

        problem, ext = os.path.splitext(os.path.basename(files[0]))
        language = KattisSubmission.LANGUAGE_GUESS.get(ext, None)
        if language is None:
            raise KattisSubmissionException(
                "Could not guess submission language. Make sure your files have the correct extensions")

        mainclass = problem if language in KattisSubmission.GUESS_MAINCLASS else None

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


class KattisSubmissionResult:
    """
    Contains logic for handling successful submission results.
    """

    @staticmethod
    def create_from_response(response):
        """
        Creates a new submission result from the response object.

        @type response: Requests response
        @param response: Response object of a returned by a submission request. 

        @rtype: KattisSubmissionResult
        @return: The submission result object created from the response
        """
        split = response.text.split(" ")
        submission_id = split[len(split) - 1][:-1]
        message = response.text
        link = config.submissionurl[:-7] + "/submissions/" + submission_id

        return KattisSubmissionResult(submission_id, message, link)

    def __init__(self, submission_id, text, link):
        """
        Instantiates a new KattisSubmissionResult object with the given parameters.

        @type submission_id: String
        @param submission_id: The id of the problem of the submission

        @type text: String
        @param: The response text of the submission

        @type link: String
        @param link: The link to the result page
        """
        self.submission_id = submission_id
        self.text = text
        self.link = link


class KattisClient:
    """
    A client for executing Kattis requests
    """

    HEADERS = {'User-Agent': 'kattis-cli-submit'}

    @staticmethod
    def create_from_config(kattis_config):
        """
        Authenticates the user with the given KattisConfig

        @type kattis_config: KattisConfig
        @param kattis_config: The KattisConfig used to authenticate with Kattis

        @rtype: KattisClient
        @return: The authenticated KattisClient
        """
        if kattis_config is None:
            raise KattisClientException(
                "No config provided. Make sure you are not passing None values")

        if kattis_config.password is None and kattis_config.token is None:
            raise KattisConfigError(
                "Your .kattisrc seems to be corrupted. Please download a new one.")

        login_args = {'user': kattis_config.username, 'script': 'true'}
        if kattis_config.password:
            login_args['password'] = kattis_config.password
        if kattis_config.token:
            login_args['token'] = kattis_config.token

        res = requests.post(kattis_config.loginurl,
                            data=login_args, headers=KattisClient.HEADERS)
        if not res.status_code == 200:
            raise KattisLoginError(
                "Could not log in to Kattis. Status code: " + res.status.code)

        return KattisClient(kattis_config, res.cookies)

    def __init__(self, kattis_config, auth_cookies):
        """
        Instantiate a new KattisClient object

        @type kattis_config: KattisConfig
        @param kattis_config: The configuration of the client

        @type auth_cookies: Dict
        @param auth_cookies: The authentication cookies obtained from Kattis
        """
        self.config = kattis_config
        self.auth_cookies = auth_cookies

    def submit_solution(self, kattis_submission):
        """
        Submits a solution to Kattis. Returns a KattisSubmissionResult on success,
        otherwise throws a KattisClientException.

        @type kattis_submission: KattisSubmission
        @param kattis_submission: The Kattis

        @raise KattisClientException: Raised when the submission is unsucessful
                                      (return code is not 200)

        @rtype: KattisSubmissionResult
        @return: The successful result of the submission
        """
        data = {'submit': 'true',
                'submit_ctr': 2,
                'language': kattis_submission.language,
                'mainclass': kattis_submission.mainclass,
                'problem': kattis_submission.problem,
                'tag': '',
                'script': 'true'}

        sub_files = []
        for f in kattis_submission.files:
            with open(f) as sub_file:
                sub_files.append(('sub_file[]',
                                  (os.path.basename(f),
                                   sub_file.read(),
                                   'application/octet-stream')))

        response = requests.post(
            self.config.submissionurl, data=data, files=sub_files,
            cookies=self.auth_cookies, headers=KattisClient.HEADERS)

        return KattisSubmissionResult.create_from_response(response)


class KattisException(Exception):
    pass


class KattisConfigException(KattisException):
    pass


class KattisSubmissionException(KattisException):
    pass


class KattisClientException(KattisException):
    pass

"""
config = KattisConfig.create_from_file()
client = KattisClient.create_from_config(config)
submission = KattisSubmission.create_from_file(["hello.py"])
result = client.submit_solution(submission)
print(result.text)
print(result.link)
"""
