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
import re
import argparse


class InvalidIndex(Exception):
    """ This exception is raised upon invalid template indexes. """

    def __init__(self, *args):
        super(InvalidIndex, self).__init__(*args)


def parse(header, footer, template, csv, separator):
    """ Parse the CSV file, and produce output based on the header, footer
    and template files. separator defines the separator used to separate the csv
    items. """

    result = header.read()

    for line in csv:
        fields = line.split(separator)
        fields = [l.strip() for l in fields]
        fields = [item for item in fields if item]

        if 0 != len(fields):
            template.seek(0)

            for tmpl in template:
                if not re.match(r'^#', tmpl):
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

    parser = argparse.ArgumentParser(description="""
Translate csv into output by, for each csv line, replacing every
occurence of %[0-9]+% in template with its respective csv column.
header and footer is prepended and appended, respectively, to the
output, which is written to stdout.""")

    parser.add_argument("-s", "--separator", type = str, default=",",
                        help = "define csv separator")
    parser.add_argument("header", type = file,
                        help = "file contents are prepended to the translation")
    parser.add_argument("footer", type = file,
                        help = "file contents are appended to the translation")
    parser.add_argument("template", type = file,
                        help = "contains the translation rules")
    parser.add_argument("csv", type = file,
                        help = "the CSV table to translate")

    try:
        args = parser.parse_args(args)
    except SystemExit as exc:
        return exc.code
    except IOError as exc:
        print "error: %s not found" % exc.filename

        parser.print_help()
        return 128

    out = parse(args.header, args.footer, args.template, args.csv,
                args.separator[0])

    print out
    return 0


if "__main__" == __name__:
    sys.exit(main(sys.argv[1:]))
