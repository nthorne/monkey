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
        """ Since we do not use the data, write does nothing. """

        pass


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

    builder = StringIO()

    save_stdout = sys.stdout
    sys.stdout = builder

    yield
    
    sys.stdout = save_stdout

    testbase.assertEquals(expected, builder.getvalue())
    #assert(expected == builder.get_string())


class MonkeyTest(mox.MoxTestBase):
    """ Test suite for monkey. """

    __monkey_args = ["monkey", "foo", "bar", "foobar", "foobaz"]

    def setUp(self):
        """ Set up variables used in test cases. """ 

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
        """ Clean up after each test case. """

        self.mox.UnsetStubs()

    def test_invalid_number_of_arguments(self):
        """ If incorrect number of arguments is passed to monkey, an error code
        shall be returned. """

        # Stub this one just to make sure that it does not get called
        self.mox.StubOutWithMock(__builtin__, "open")

        self.mox.ReplayAll()

        with nostdout(): 
            self.assertEquals(1, monkey.main(["monkey", "foo"]))
            self.assertEquals(1, monkey.main(["monkey", "foo", "bar"]))
            self.assertEquals(1, monkey.main(["monkey", "foo", "bar",
                                              "foobar"]))

    def test_failing_to_open_header_file(self):
        """ If monkey fails to open the header file, an error code shall be
        returned. """

        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndRaise(IOError)

        self.mox.ReplayAll()

        with nostdout():
            self.assertEquals(2, monkey.main(self.__monkey_args))

    def test_failing_to_open_footer_file(self):
        """ If monkey fails to open the footer file, an error code shall be
        returned. """

        mock_file = self.mox.CreateMockAnything()

        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndReturn(mock_file)
        __builtin__.open("bar").AndRaise(IOError)

        self.mox.ReplayAll()

        with nostdout():
            self.assertEquals(2, monkey.main(self.__monkey_args))

    def test_failing_to_open_template_file(self):
        """ If monkey fails to open the template file, an error code shall be
        returned. """

        mock_file = self.mox.CreateMockAnything()

        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndReturn(mock_file)
        __builtin__.open("bar").AndReturn(mock_file)
        __builtin__.open("foobar").AndRaise(IOError)

        self.mox.ReplayAll()

        with nostdout():
            self.assertEquals(2, monkey.main(self.__monkey_args))

    def test_failing_to_open_csv_file(self):
        """ If monkey fails to open the csv file, an error code shall be
        returned. """

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
        """ Make sure that the help flags are accepted. """

        with nostdout():
            self.assertEquals(0, monkey.main(["monkey", "-h"]))
            self.assertEquals(0, monkey.main(["monkey", "--help"]))

    def test_simple_translation(self):
        """ Ensure that a basic CSV translation works as expected. """

        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndReturn(self.__header)
        __builtin__.open("bar").AndReturn(self.__footer)
        __builtin__.open("foobar").AndReturn(self.__template)
        __builtin__.open("foobaz").AndReturn(self.__csv)

        self.mox.ReplayAll()

        with stdoutcomparator(self, self.__expected_output_simple):
            self.assertEquals(0, monkey.main(self.__monkey_args))

    def test_translation_zero_index(self):
        """ If a 0 index is encountered in the template file, an InvalidIndex
        exception shall be raised. """

        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndReturn(self.__header)
        __builtin__.open("bar").AndReturn(self.__footer)
        __builtin__.open("foobar").AndReturn(self.__template_zero_index)
        __builtin__.open("foobaz").AndReturn(self.__csv)

        self.mox.ReplayAll()

        self.assertRaises(monkey.InvalidIndex, monkey.main, self.__monkey_args)

    def test_translation_invalid_index(self):
        """ If an invalid index (out of range) is encountered in the template
        file, an InvalidIndex exception shall be raised. """

        self.mox.StubOutWithMock(__builtin__, "open")

        __builtin__.open("foo").AndReturn(self.__header)
        __builtin__.open("bar").AndReturn(self.__footer)
        __builtin__.open("foobar").AndReturn(self.__template_invalid_index)
        __builtin__.open("foobaz").AndReturn(self.__csv)

        self.mox.ReplayAll()

        self.assertRaises(monkey.InvalidIndex, monkey.main, self.__monkey_args)

    def test_translation_duplicate_indedxes(self):
        """ Duplicated indexes in the template file should be accepted. """

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
