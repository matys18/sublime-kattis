import pytest
import os
from sublime_kattis.kattis import *

# Guide to running the tests:
# 1: Remove all of your existing .kattisrc files that you have (including current and home directory)
# 2: Place a valid .kattisrc file in the current directory
# 3: Make sure hello.py is still present in the current directory
# 4: Run this file with pytest

@pytest.fixture(scope="module")
def kattisrc():
    if not os.path.isfile(".kattisrc"):
            raise RuntimeError("No .kattisrc file found in current directory")

    yield ".kattisrc"
    if not os.path.isfile(".kattisrc"):
        os.rename("kattisrc", ".kattisrc")

@pytest.fixture(scope="module")
def hellopy():
    if not os.path.isfile("hello.py"):
            raise RuntimeError("No hello.py file found in current directory")

    yield "hello.py"
    if not os.path.isfile("hello.py"):
        os.rename("hellopy", "hello.py")

@pytest.mark.usefixtures("kattisrc")
class TestKattisConfig:

    def test_create_from_file(self, kattisrc):
        """
        Tests that .kattisrc files can be found and parsed correctly
        """
        if not os.path.isfile(kattisrc):
            raise RuntimeError("No .kattisrc file found in current directory")

        # Rename .kattisrc file and check that we get an exception
        os.rename(kattisrc, "kattisrc")
        with pytest.raises(KattisConfigException) as exception:
            KattisConfig.create_from_file()

        # Check that we can generate a KattisConfig using a custom path
        config = KattisConfig.create_from_file("kattisrc")
        self.config_test_helper(config)

        # Rename the file back to what it was and check that it finds the file
        os.rename("kattisrc", kattisrc)
        config = KattisConfig.create_from_file()
        self.config_test_helper(config)

    def config_test_helper(self, config):
        assert isinstance(config, KattisConfig)
        assert isinstance(config.username, str)
        assert isinstance(config.loginurl, str)
        assert isinstance(config.submissionurl, str)
        assert isinstance(config.token, str) or isinstance(config.password, str)

@pytest.mark.usefixtures("hellopy")
class TestKattisSubmission:

    def test_create_from_file(self, hellopy):
        """
        This does not test for every single language type.
        It exists purely to make sure that basic functionallity
        of the method is not compromised.
        """
        submission = KattisSubmission.create_from_file([hellopy])
        assert submission.problem == "hello"
        assert "Python" in submission.language
        assert len(submission.files) > 0

        os.rename(hellopy, "hellopy")
        with pytest.raises(KattisSubmissionException) as exception:
            KattisSubmission.create_from_file([hellopy])
        os.rename("hellopy", hellopy)

        with pytest.raises(KattisSubmissionException) as exception:
            KattisSubmission.create_from_file([])

class TestKattisClient:

    def test_create_from_config(self):
        # Test with no config
        with pytest.raises(KattisClientException) as exception:
            KattisClient.create_from_config(None)

        # Test with a corrupted mock config
        config = KattisConfig.create_from_file()
        config.username = None
        config.token = None
        config.password = None

        with pytest.raises(KattisConfigException) as exception:
            KattisClient.create_from_config(config)

        # Test with an invalid config
        config.username = "kekekekekke"
        config.token = "oifnoweifnwiefn"

        with pytest.raises(KattisClientException) as exception:
            KattisClient.create_from_config(config)

        # Test with a valid config
        config = KattisConfig.create_from_file()
        client = KattisClient.create_from_config(config)
        assert isinstance(client, KattisClient)
        assert client.auth_cookies is not None

    def test_submit_solution(self):
        """
        This test is tricky since Kattis might rate limit
        you to a one submission every few seconds.
        """
        config = KattisConfig.create_from_file()
        client = KattisClient.create_from_config(config)

        # Check that basic submitting works
        submission = KattisSubmission.create_from_file(["hello.py"])
        result = client.submit_solution(submission)
        assert isinstance(result, KattisSubmissionResult)
        assert isinstance(result.text, str)
        assert isinstance(result.link, str)
        assert isinstance(result.submission_id, str)





