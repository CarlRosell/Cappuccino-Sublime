# -*- coding: utf-8 -*-
# balance_brackets.py
#
# (c) 2014 Aparajita Fishman and licensed under the MIT license.
# URL: http://github.com/aparajita
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

"""This module provides the BalanceBracketsCommand class."""

import sublime
import sublime_plugin
import os
import os.path
import subprocess
from . import util

PARSER = 'lib/objj_parser.rb'


class BalanceBracketsCommand(sublime_plugin.TextCommand):

    """This class implements a command which inserts square brackets intelligently."""

    ruby_path = None
    have_parser = False

    @classmethod
    def init(cls):
        """Set up our environment so we can execute the ruby parser."""
        cls.ruby_path = None
        cls.have_parser = False

        path = util.PACKAGE + '/Cappuccino.sublime-settings'
        util.copy_resource(path, 'Cappuccino.sublime-settings', overwrite=False)

        version = cls.find_ruby()

        if version is not None:
            print('Cappuccino: using \'{}\' ({})'.format(cls.ruby_path, version))
            if cls.copy_parser():
                cls.have_parser = True

    @staticmethod
    def ruby_version(path):
        """Return the version of the ruby at the given path if it exists, else None."""

        try:
            if os.name == 'nt':
                info = subprocess.STARTUPINFO()
                info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                info.wShowWindow = subprocess.SW_HIDE
            else:
                info = None

            version = subprocess.check_output([path, '--version'], startupinfo=info).decode().strip()
            return version
        except:
            return None

    @classmethod
    def find_ruby(cls):
        """
        Try to locate a copy of ruby we can execute, return success.

        First settings are consulted for "cappuccino_ruby_path".
        If that is not set or is not valid, we try "ruby".
        """
        settings = sublime.load_settings('Cappuccino.sublime-settings')
        settings.clear_on_change('Cappuccino')
        settings.add_on_change('Cappuccino', cls.init)
        path = settings.get('ruby_path')

        if path:
            path = os.path.expanduser(path)
            version = cls.ruby_version(path)

            if version is not None:
                cls.ruby_path = path
                return version
            else:
                print('Cappuccino: no such ruby at \'{}\''.format(path))

        version = cls.ruby_version('ruby')

        if version is not None:
            cls.ruby_path = 'ruby'
            return version

        print('Cappuccino: could not find a ruby to execute')
        return None

    @classmethod
    def copy_parser(cls):
        """Copy the Objective-J parser to Packages/User."""
        return util.copy_resource(util.PACKAGE + '/Support/' + PARSER, util.PACKAGE + '/' + PARSER)

    def is_enabled(self):
        """Return enabled only if editing Objective-J code."""
        return (
            self.ruby_path is not None and
            self.have_parser and
            self.view.settings().get('syntax').endswith('/Objective-J.tmLanguage')
        )

    def run(self, edit):
        """Run the command."""
        selections = self.view.sel()

        # For now we don't try to balance multiple or non-empty selections, just insert as usual
        if len(selections) > 1:
            for selection in reversed(selections):
                self.insert(edit, selection)
            return

        selection = selections[0]

        if not selection.empty():
            self.insert(edit, selection)
            return

        point = selection.end()
        line = self.view.line(point)
        text = self.view.substr(line)

        if not text.strip():
            self.insert(edit, selection)
            return

        col = self.view.rowcol(point)[1]

        os.environ['TM_CURRENT_LINE'] = text
        os.environ['TM_LINE_INDEX'] = str(col)

        if os.name == 'nt':
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = subprocess.SW_HIDE
        else:
            info = None

        pipe = subprocess.Popen(
            ['ruby', self.parser_path()],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=info)

        result = pipe.communicate()

        if result[1]:
            print(
                'Cappuccino: Objective-J parser returned an error for the line:\n{}\n\nError message:\n{}'
                .format(text, str(result[1], 'utf-8'))
            )
            snippet = text[0:col] + ']$0' + text[col:]
        else:
            snippet = str(result[0], 'utf-8')

        self.view.erase(edit, line)
        self.view.run_command('insert_snippet', {'contents': snippet})

    @staticmethod
    def parser_path():
        """Return the path to the ruby Objective-J parser."""
        return os.path.join(sublime.packages_path(), 'User', util.PACKAGE, PARSER)

    def insert(self, edit, selection):
        """
        Handle inserts of ']'.

        If the selection is empty and the character to the right of the cursor is ']',
        then replace it, don't insert another one. This is standard ST behavior.
        """
        if selection.empty() and self.view.substr(selection.end()) == ']':
            selection = sublime.Region(selection.begin(), selection.begin() + 1)

        point = selection.begin()
        self.view.erase(edit, selection)
        self.view.insert(edit, point, ']')


def plugin_loaded():
    """Called when the plugin has been loaded by ST."""
    sublime.set_timeout_async(BalanceBracketsCommand.init())
