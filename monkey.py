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
    """ This exception is raised upon invalid template indexes. """

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


def parse(header, footer, template, csv):
    """ Parse the CSV file, and produce output based on the header, footer
    and template files. """

    result = header.read()

    for line in csv:
        fields = line.split(",")
        fields = [l.strip() for l in fields]
        fields = [item for item in fields if item]

        if 0 != len(fields):
            template.seek(0)

            for tmpl in template:
                matches = re.findall('%[0-9]+%', tmpl)
                if matches:
                    for match in matches:
                        index = int(match.strip().strip('%'))

                        if 0 == index:
                            raise InvalidIndex("invalid template index: 0")
                        try:
                            tmpl = tmpl.replace(match.strip(),
                                                fields[index - 1])
                        except:
                            raise InvalidIndex(
                                "invalid template index: %d" % index)
                result += tmpl

    result += footer.read()

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
        footer = open(args[2])
        template = open(args[3])
        csv = open(args[4])
    except IOError as exc:
        print "error: %s not found" % exc.filename
        print
        print_usage()
        return 2

    out = parse(header, footer, template, csv)

    header.close()
    footer.close()
    template.close()
    csv.close()

    print out
    return 0

if "__main__" == __name__:
    sys.exit(main(sys.argv))
