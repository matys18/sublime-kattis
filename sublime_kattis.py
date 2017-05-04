import sublime
import sublime_plugin
import subprocess
import os
import sys

from sublime_kattis.submit import Kattis

class KattisCommand(sublime_plugin.WindowCommand):
    
    def run(self):
        self.loading_key = "sublime-kattis-loading"
        self.submit()
        #submission_info = self.prepare_submission()
        #self.display_confirm_dialog(submission_info)

    # Submits the solution to Kattis
    def submit(self):
        self.window.status_message("Submitting to Kattis")
        variables = self.window.extract_variables()
        path = os.path.join(variables["file_path"], variables["file_name"])
        res = Kattis(path).submit_solution()
        print(res)
        self.window.status_message("Submission successful!")
        


    # Prompts the user to review submission info.
    # Returns true if user clicked "Submit", false otherwise
    def display_confirm_dialog(self, submission_info):
        return sublime.ok_cancel_dialog(submission_info, "Submit")