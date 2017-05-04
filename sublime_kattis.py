import sublime
import sublime_plugin
import subprocess
import os
import sys

from sublime_kattis.submit import Kattis, KattisSubmission, KattisException


class KattisCommand(sublime_plugin.WindowCommand):

    def run(self):
        self.loading_key = "sublime-kattis-loading"
        self.submit()

    # Submits the solution to Kattis
    def submit(self):
        self.window.status_message("Submitting to Kattis")
        variables = self.window.extract_variables()
        path = os.path.join(variables["file_path"], variables["file_name"])
        try:
            kattis = Kattis()
            sub = kattis.prepare_submission(path)
            self.display_confirm_dialog(sub)
            res = kattis.submit_solution(sub)
            view = self.window.new_file()
            view.run_command("kattisresult", {"displayText": res.text})
        except KattisException as e:
            view = self.window.new_file()
            view.run_command("kattisresult", {
                             "displayText": "Kattis submission error: " + format(e)})

    # Prompts the user to review submission info.
    # Returns true if user clicked "Submit", false otherwise
    def display_confirm_dialog(self, submission):
        submission_info = (
            "Submission details:\n\nProblem: " + submission.problem +
            "\nLanguage: " + submission.language +
            "\nFiles: " + submission.files[0]
        )
        return sublime.ok_cancel_dialog(submission_info, "Submit")


class KattisresultCommand(sublime_plugin.TextCommand):

    def run(self, edit, **kwargs):
        self.view.insert(edit, 0, kwargs["displayText"])
