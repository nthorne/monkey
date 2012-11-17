#!/usr/bin/env python

#Copyright (C) 2012 Niklas Thorne.

#This file is part of monkey.
#
#monkey is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#monkey is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with monkey.  If not, see <http://www.gnu.org/licenses/>.

""" monkey is a utility for translating CSV files based on template rules. """

import sys
import os
import re


class InvalidIndex(Exception):
    def __init__(self, *args):
        super(InvalidIndex, self).__init__(*args)

def print_usage():
    """ Display help text. """

    print "usage:", os.path.basename(sys.argv[0]), "HEADER FOOTER TEMPLATE CSV"
    print
    print "Translate CSV into output by, for each CSV line, replacing every"
    print "occurence of %[0-9]+% in TEMPLATE with its respective CSV column."
    print "HEADER and FOOTER is prepended and appended, respectively, to the"
    print "output, which is written to stdout"


class Parser:
    """ This type implements the CSV parser. """

    def __init__(self, header, footer, template, csv):
        self.__header = header
        self.__footer = footer
        self.__template = template
        self.__csv = csv

    def parse(self):
        """ Parse the CSV file, and produce output based on the header, footer
        and template files. """

        result = self.__header.read()

        for line in self.__csv:
            fields = line.split(",")
            fields = [l.strip() for l in fields]
            fields = [item for item in fields if item]

            if 0 != len(fields):
                self.__template.seek(0)

                for tmpl in self.__template:
                    matches = re.findall('%[0-9]+%', tmpl)
                    if matches:
                        for match in matches:
                            index = int(match.strip().strip('%'))
                            try:
                                tmpl = tmpl.replace(match.strip(),
                                                    fields[index - 1])
                            except:
                                sys.stderr.write("no item %d (%s), in %s\n"
                                                 %(index, tmpl.rstrip(),
                                                   fields))
                    result += tmpl

        result += self.__footer.read()

        return result


def main(args):
    """ Avoid polluting the global namespace. """

    if 5 != len(args):
        if 2 == len(args) and ("-h" == args[1] or "--help" == args[1]):
            print_usage()
            return 0
        else:
            print_usage()
            return 1

    try:
        header = open(args[1])
    except:
        print "error: header file", args[1], "not found."
        print
        print_usage()
        return 2

    try:
        footer = open(args[2])
    except:
        print "error: footer file", args[2], "not found."
        print
        print_usage()
        return 2

    try:
        template = open(args[3])
    except:
        print "error: template file", args[3], "not found."
        print
        print_usage()
        return 2

    try:
        csv = open(args[4])
    except:
        print "error: csv", args[4], "not found."
        print
        print_usage()
        return 2

    parser = Parser(header, footer, template, csv)

    out = parser.parse()

    header.close()
    footer.close()
    template.close()
    csv.close()

    print out
    return 0

if "__main__" == __name__:
    sys.exit(main(sys.argv))
