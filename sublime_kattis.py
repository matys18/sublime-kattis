import sublime
import sublime_plugin
import subprocess
import os
import sys

from sublime_kattis.kattis import (KattisConfig, KattisClient, KattisSubmission,
                                   KattisSubmissionResult, KattisException)


class KattisCommand(sublime_plugin.WindowCommand):
    """
    Created when the user executes the Kattis command.
    """

    def run(self):
        self.submit()

    def submit(self):
        """
        Submits the current file to Kattis
        """
        self.window.status_message("Submitting to Kattis")
        variables = self.window.extract_variables()
        path = os.path.join(variables["file_path"], variables["file_name"])
        try:
            config = KattisConfig.create_from_file()
            submission = KattisSubmission.create_from_file([path])

            self.display_confirm_dialog(submission)

            client = KattisClient.create_from_config(config)
            result = client.submit_solution(submission)

            view = self.window.new_file()
            displayText = result.text + "\nSubmission url: " + result.link
            view.run_command("kattisresult", {"displayText": displayText})
        except KattisException as e:
            view = self.window.new_file()
            view.run_command("kattisresult", {
                             "displayText": "Kattis submission error: " + format(e)})

    def display_confirm_dialog(self, submission):
        """
        Prompts the user to review submission info.
        Returns true if user clicked "Submit", false otherwise
        """
        submission_info = (
            "Submission details:\n\nProblem: " + submission.problem +
            "\nLanguage: " + submission.language +
            "\nFiles: " + submission.files[0]
        )
        return sublime.ok_cancel_dialog(submission_info, "Submit")


class KattisresultCommand(sublime_plugin.TextCommand):
    """
    Created when the user executes the Kattisresult command.
    """

    def run(self, edit, **kwargs):
        self.view.insert(edit, 0, kwargs["displayText"])
