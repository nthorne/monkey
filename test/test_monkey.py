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
import contextlib
from StringIO import StringIO

import argparse


class DummyFile(object):
    """ This type is used to provide a NOOP writem for suppressing output to
    stdout. """

    def write(self, data):
        """ Since we do not use the data, write does nothing. """

        pass


@contextlib.contextmanager
def nostdoutstderr():
    """ This context is used to suppress output to stdout and stderr. """
    save_stdout = sys.stdout
    save_stderr = sys.stderr

    sys.stdout = DummyFile()
    sys.stderr = DummyFile()

    yield

    sys.stderr = save_stderr
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

    __monkey_args = ["foo", "bar", "foobar", "foobaz"]
    __monkey_args_changed_separator = ["-s=.", "foo", "bar", "foobar", "foobaz"]

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

        self.__csv_dot_separator = StringIO("FIRST.SECOND")

    def mock_reading_files(self, args, index_file_contents):
        """ help method used to mock reading the defined files, where the
        template file contents may vary. """

        self.mox.StubOutWithMock(argparse.ArgumentParser, "_get_value")

        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           mox.IgnoreArg()).AndReturn(",")
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           args[0]).AndReturn(self.__header)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           args[1]).AndReturn(self.__footer)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           args[2]).AndReturn(index_file_contents)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           args[3]).AndReturn(self.__csv)
    def tearDown(self):
        """ Clean up after each test case. """

        self.mox.UnsetStubs()

    def test_invalid_number_of_arguments(self):
        """ If incorrect number of arguments is passed to monkey, an error code
        shall be returned. """

        mock_file = self.mox.CreateMockAnything()

        self.mox.StubOutWithMock(argparse.ArgumentParser, "_get_value")

        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           mox.IgnoreArg()).AndReturn(",")
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foo").AndReturn(mock_file)

        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           mox.IgnoreArg()).AndReturn(",")
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foo").AndReturn(mock_file)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "bar").AndReturn(mock_file)

        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           mox.IgnoreArg()).AndReturn(",")
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foo").AndReturn(mock_file)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "bar").AndReturn(mock_file)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foobar").AndReturn(mock_file)

        self.mox.ReplayAll()

        with nostdoutstderr(): 
            self.assertEquals(2, monkey.main(["foo"]))
            self.assertEquals(2, monkey.main(["foo", "bar"]))
            self.assertEquals(2, monkey.main(["foo", "bar", "foobar"]))

    def test_failing_to_open_header_file(self):
        """ If monkey fails to open the header file, an error code shall be
        returned. """

        self.mox.StubOutWithMock(argparse.ArgumentParser, "_get_value")

        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           mox.IgnoreArg()).AndReturn(",")
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foo").AndRaise(IOError)

        self.mox.ReplayAll()

        with nostdoutstderr():
            self.assertEquals(128, monkey.main(self.__monkey_args))

    def test_failing_to_open_footer_file(self):
        """ If monkey fails to open the footer file, an error code shall be
        returned. """

        mock_file = self.mox.CreateMockAnything()

        self.mox.StubOutWithMock(argparse.ArgumentParser, "_get_value")

        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           mox.IgnoreArg()).AndReturn(",")
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foo").AndReturn(mock_file)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "bar").AndRaise(IOError)

        self.mox.ReplayAll()

        with nostdoutstderr():
            self.assertEquals(128, monkey.main(self.__monkey_args))

    def test_failing_to_open_template_file(self):
        """ If monkey fails to open the template file, an error code shall be
        returned. """

        mock_file = self.mox.CreateMockAnything()

        self.mox.StubOutWithMock(argparse.ArgumentParser, "_get_value")

        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           mox.IgnoreArg()).AndReturn(",")
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foo").AndReturn(mock_file)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "bar").AndReturn(mock_file)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foobar").AndRaise(IOError)

        self.mox.ReplayAll()

        with nostdoutstderr():
            self.assertEquals(128, monkey.main(self.__monkey_args))

    def test_failing_to_open_csv_file(self):
        """ If monkey fails to open the csv file, an error code shall be
        returned. """

        mock_file = self.mox.CreateMockAnything()

        self.mox.StubOutWithMock(argparse.ArgumentParser, "_get_value")

        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           mox.IgnoreArg()).AndReturn(",")
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foo").AndReturn(mock_file)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "bar").AndReturn(mock_file)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foobar").AndReturn(mock_file)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foobaz").AndRaise(IOError)

        self.mox.ReplayAll()

        with nostdoutstderr():
            self.assertEquals(128, monkey.main(self.__monkey_args))

    def test_help_command(self):
        """ Make sure that the help flags are accepted. """

        with nostdoutstderr():
            self.assertEquals(0, monkey.main(["-h"]))
            self.assertEquals(0, monkey.main(["--help"]))

    def test_simple_translation(self):
        """ Ensure that a basic CSV translation works as expected. """

        self.mock_reading_files(self.__monkey_args,
                                self.__template)

        self.mox.ReplayAll()

        with stdoutcomparator(self, self.__expected_output_simple):
            self.assertEquals(0, monkey.main(self.__monkey_args))

    def test_translation_zero_index(self):
        """ If a 0 index is encountered in the template file, an InvalidIndex
        exception shall be raised. """

        self.mock_reading_files(self.__monkey_args,
                                self.__template_zero_index)

        self.mox.ReplayAll()

        self.assertRaises(monkey.InvalidIndex, monkey.main, self.__monkey_args)

    def test_translation_invalid_index(self):
        """ If an invalid index (out of range) is encountered in the template
        file, an InvalidIndex exception shall be raised. """

        self.mock_reading_files(self.__monkey_args,
                                self.__template_invalid_index)

        self.mox.ReplayAll()

        self.assertRaises(monkey.InvalidIndex, monkey.main, self.__monkey_args)

    def test_translation_duplicate_indedxes(self):
        """ Duplicated indexes in the template file should be accepted. """


        self.mock_reading_files(self.__monkey_args,
                                self.__template_duplicated_index)

        self.mox.ReplayAll()

        with stdoutcomparator(self, self.__expected_output_duplicated):
            self.assertEquals(0, monkey.main(self.__monkey_args))

    def test_changing_csv_separator(self):
        """ Ensure translation, when having changed CSV separator, works as
        expected. """


        self.mox.StubOutWithMock(argparse.ArgumentParser, "_get_value")

        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           mox.IgnoreArg()).AndReturn(".")
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           mox.IgnoreArg()).AndReturn(".")
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foo").AndReturn(self.__header)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "bar").AndReturn(self.__footer)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foobar").AndReturn(self.__template)
        argparse.ArgumentParser._get_value(mox.IgnoreArg(),
                                           "foobaz").AndReturn(
                                               self.__csv_dot_separator)
        self.mox.ReplayAll()

        with stdoutcomparator(self, self.__expected_output_simple):
            self.assertEquals(0,
                              monkey.main(self.__monkey_args_changed_separator))


if "__main__" == __name__:
    unittest.main()
