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

# Imported in order to be able to mock open()
import __builtin__

import sys
import os

sys.path.append(os.path.abspath(".."))

import mox
import unittest
import monkey
import contextlib
from StringIO import StringIO


class DummyFile(object):
    """ This type is used to provide a NOOP writem for suppressing output to
    stdout. """
    def write(self, data):
        pass

class StringBuilder(object):
    def __init__(self):
        self.__str = ""

    def write(self, data):
        self.__str += data

    def get_string(self):
        return self.__str

@contextlib.contextmanager
def nostdout():
    """ This context is used to suppress output to stdout. """
    save_stdout = sys.stdout
    sys.stdout = DummyFile()

    yield

    sys.stdout = save_stdout

@contextlib.contextmanager
def stdoutcomparator(testbase, expected):
    """ This context is used to compare generated stdout against an expected
    value. """

    builder = StringBuilder()

    save_stdout = sys.stdout
    sys.stdout = builder

    yield
    
    sys.stdout = save_stdout

    testbase.assertEquals(expected, builder.get_string())
    #assert(expected == builder.get_string())


class MonkeyTest(mox.MoxTestBase):

    __monkey_args = ["monkey", "foo", "bar", "foobar", "foobaz"]

    def setUp(self):
        self.mox = mox.Mox()

        self.__header = StringIO("HEADER")
        self.__footer = StringIO("FOOTER")

        self.__csv = StringIO("FIRST,SECOND")
        self.__template = StringIO("%1% and %2%")
        self.__template_zero_index = StringIO("%0% and %1% and %2%")
        self.__template_invalid_index = StringIO("%1% and %2% and %3%")
        self.__template_duplicated_index = StringIO("%1% and %1%")

        self.__expected_output_simple = "%sFIRST and SECOND%s\n" % \
                (self.__header.getvalue(), self.__footer.getvalue()) 
        self.__expected_output_duplicated = "%sFIRST and FIRST%s\n" % \
                (self.__header.getvalue(), self.__footer.getvalue()) 

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_invalid_number_of_arguments(self):
        # Stub this one just to make sure that it does not get called
        self.mox.StubOutWithMock(__builtin__, "open")

        self.mox.ReplayAll()

        with nostdout(): 
            self.assertEquals(1, monkey.main(["monkey", "foo"]))
            self.assertEquals(1, monkey.main(["monkey", "foo", "bar"]))
            self.assertEquals(1, monkey.main(["monkey", "foo", "bar",
                                              "foobar"]))

    def test_failing_to_open_header_file(self):
        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndRaise(IOError)

        self.mox.ReplayAll()

        with nostdout():
            self.assertEquals(2, monkey.main(self.__monkey_args))

    def test_failing_to_open_footer_file(self):
        mock_file = self.mox.CreateMockAnything()

        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndReturn(mock_file)
        __builtin__.open("bar").AndRaise(IOError)

        self.mox.ReplayAll()

        with nostdout():
            self.assertEquals(2, monkey.main(self.__monkey_args))

    def test_failing_to_open_template_file(self):
        mock_file = self.mox.CreateMockAnything()

        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndReturn(mock_file)
        __builtin__.open("bar").AndReturn(mock_file)
        __builtin__.open("foobar").AndRaise(IOError)

        self.mox.ReplayAll()

        with nostdout():
            self.assertEquals(2, monkey.main(self.__monkey_args))

    def test_failing_to_open_csv_file(self):
        mock_file = self.mox.CreateMockAnything()

        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndReturn(mock_file)
        __builtin__.open("bar").AndReturn(mock_file)
        __builtin__.open("foobar").AndReturn(mock_file)
        __builtin__.open("foobaz").AndRaise(IOError)

        self.mox.ReplayAll()

        with nostdout():
            self.assertEquals(2, monkey.main(self.__monkey_args))

    def test_help_command(self):
        with nostdout():
            self.assertEquals(0, monkey.main(["monkey", "-h"]))
            self.assertEquals(0, monkey.main(["monkey", "--help"]))

    def test_simple_translation(self):
        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndReturn(self.__header)
        __builtin__.open("bar").AndReturn(self.__footer)
        __builtin__.open("foobar").AndReturn(self.__template)
        __builtin__.open("foobaz").AndReturn(self.__csv)

        self.mox.ReplayAll()

        with stdoutcomparator(self, self.__expected_output_simple):
            self.assertEquals(0, monkey.main(self.__monkey_args))

    def test_translation_zero_index(self):
        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndReturn(self.__header)
        __builtin__.open("bar").AndReturn(self.__footer)
        __builtin__.open("foobar").AndReturn(self.__template_zero_index)
        __builtin__.open("foobaz").AndReturn(self.__csv)

        self.mox.ReplayAll()

        self.assertRaises(monkey.InvalidIndex, monkey.main, self.__monkey_args)

    def test_translation_invalid_index(self):
        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndReturn(self.__header)
        __builtin__.open("bar").AndReturn(self.__footer)
        __builtin__.open("foobar").AndReturn(self.__template_invalid_index)
        __builtin__.open("foobaz").AndReturn(self.__csv)

        self.mox.ReplayAll()

        self.assertRaises(monkey.InvalidIndex, monkey.main, self.__monkey_args)

    def test_translation_duplicate_indedxes(self):
        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndReturn(self.__header)
        __builtin__.open("bar").AndReturn(self.__footer)
        __builtin__.open("foobar").AndReturn(self.__template_duplicated_index)
        __builtin__.open("foobaz").AndReturn(self.__csv)

        self.mox.ReplayAll()

        with stdoutcomparator(self, self.__expected_output_duplicated):
            self.assertEquals(0, monkey.main(self.__monkey_args))


if "__main__" == __name__:
    unittest.main()
