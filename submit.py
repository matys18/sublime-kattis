import requests
import sys
import os

# Python 2/3 compatibility
if sys.version_info[0] >= 3:
    import configparser
else:
    # Python 2, import modules with Python 3 names
    import ConfigParser as configparser

_VERSION = 'Version: $Version: $'
_LANGUAGE_GUESS = {
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
_GUESS_MAINCLASS = {'Java', 'Python'}
_HEADERS = {'User-Agent': 'kattis-cli-submit'}

class Kattis:

    def __init__(self, path):
        self.path = path # Path of the file to submit
        self.cfg = self.read_config()
        self.credentials = self.login_with_config()
        self.language = self.guess_language()
        self.mainclass = self.guess_class()
        self.problem = self.guess_problem()
        self.files = [self.path]

    def submit_solution(self):
        submission_res = self.submit(
            self.credentials,
            self.problem,
            self.language,
            self.files,
            self.mainclass
        )
        return submission_res.text

    def guess_language(self):
        problem, ext = os.path.splitext(os.path.basename(self.path))
        language = _LANGUAGE_GUESS.get(ext, None)

        if language == 'Python':
            python_version = str(sys.version_info[0])
            try:
                python_version = self.cfg.get('defaults', 'python-version')
            except configparser.Error:
                pass

            if python_version not in ['2', '3']:
                raise KattisSubmissionError("Invalid Python version specified in .kattisrc, must be 2 or 3")
            language = 'Python ' + python_version

        if language is None:
            raise KattisSubmissionError("Could not guess submission language")

        return language

    def guess_class(self):
        problem, ext = os.path.splitext(os.path.basename(self.path))
        mainclass = problem if self.language in _GUESS_MAINCLASS else None
        return mainclass

    def guess_problem(self):
        problem, ext = os.path.splitext(os.path.basename(self.path))
        return problem


    def read_config(self):
        default = "/usr/local/etc/kattisrc"
        cfg = configparser.ConfigParser()
        if os.path.exists(default):
            cfg.read(default)

        if not cfg.read([os.path.join(os.getenv('HOME'), '.kattisrc'),
                         os.path.join(os.path.dirname(os.path.expanduser("~")), '.kattisrc')]):
            raise KattisConfigError("Could not locate .kattisrc! Make sure it is placed under your home directory!")
        return cfg

    def login_with_config(self):
        username = self.cfg.get('user', 'username')
        password = token = None

        try:
            password = self.cfg.get('user', 'password')
        except configparser.NoOptionError:
            pass
        try:
            token = self.cfg.get('user', 'token')
        except configparser.NoOptionError:
            pass

        if password is None and token is None:
            raise KattisConfigError("Your .kattisrc seems to be corrupted. Please download a new one.")

        loginurl = self.get_url(self.cfg, 'loginurl', 'login')
        return self.login(loginurl, username, password, token)

    def login(self, login_url, username, password=None, token=None):
        login_args = {'user': username, 'script': 'true'}
        if password:
            login_args['password'] = password
        if token:
            login_args['token'] = token

        res = requests.post(login_url, data=login_args, headers=_HEADERS)
        if not res.status_code == 200:
            raise KattisLoginError("Could not log in to Kattis. Status code: " + res.status.code)
        return res.cookies

    def submit(self, cookies, problem, language, files, mainclass='', tag=''):
        submit_url = self.get_url(self.cfg, 'submissionurl', 'submit')
        data = {'submit': 'true',
                'submit_ctr': 2,
                'language': language,
                'mainclass': mainclass,
                'problem': problem,
                'tag': tag,
                'script': 'true'}

        sub_files = []
        for f in files:
            with open(f) as sub_file:
                sub_files.append(('sub_file[]',
                                  (os.path.basename(f),
                                   sub_file.read(),
                                   'application/octet-stream')))

        return requests.post(submit_url, data=data, files=sub_files, cookies=cookies, headers=_HEADERS)

    def get_url(self, cfg, option, default):
        if cfg.has_option('kattis', option):
            return cfg.get('kattis', option)
        else:
            return 'https://%s/%s' % (cfg.get('kattis', 'hostname'), default)

class KattisException(Exception):
    pass

class KattisConfigError(KattisException):
    pass

class KattisLoginError(KattisException):
    pass

class KattisSubmissionError(KattisException):
    pass
