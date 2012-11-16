#!/usr/bin/env python

#Copyright (C) 2012 Niklas Thorne.

#This file is part of monkey.
#
#Foobar is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#Foobar is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with Foobar.  If not, see <http://www.gnu.org/licenses/>.


""" This module tests the monkey module. """

import sys
import os

sys.path.append(os.path.abspath(".."))

import mox
import unittest
import monkey

class MonkeyTest(mox.MoxTestBase):
    def test_invalid_number_of_arguments(self):
        self.fail("Test case not implemented")

    def test_failing_to_open_header_file(self):
        self.fail("Test case not implemented")

    def test_failing_to_open_footer_file(self):
        self.fail("Test case not implemented")

    def test_failing_to_open_template_file(self):
        self.fail("Test case not implemented")

    def test_failing_to_open_csv_file(self):
        self.fail("Test case not implemented")

    def test_command_line_argument_parsing(self):
        self.fail("Test case not implemented")

    def test_translation(self):
        self.fail("Test case not implemented")

    def test_translation_invalid_index(self):
        self.fail("Test case not implemented")

    def test_translation_duplicate_indedxes(self):
        self.fail("Test case not implemented")


if "__main__" == __name__:
    unittest.main()
