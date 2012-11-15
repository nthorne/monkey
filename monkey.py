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


import sys
import os
import re

from StringIO import StringIO


def print_usage():
  print "usage:", os.path.basename(sys.argv[0]), "HEADER FOOTER TEMPLATE CSV"
  print
  print "Translate CSV into output by, for each CSV line, replacing every"
  print "occurence of %[0-9]+% within TEMPLATE with its respective CSV column."
  print "HEADER and FOOTER is prepended and appended, respectively, to the output,"
  print "which is written to stdout"


class Parser:
  def __init__(self, header, footer, template, csv):
    self.__header = header
    self.__footer = footer
    self.__template = template
    self.__csv = csv

  def parse(self):
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
                tmpl = tmpl.replace(match.strip(), fields[index - 1])
              except:
                sys.stderr.write("Failed to access index %d for line %s, csv %s\n"
                  %(index, tmpl, fields))
          result += tmpl

    result += self.__footer.read()

    return result


if "__main__" == __name__:
  if 5 != len(sys.argv) or '-h' == sys.argv[1] or '--help' == sys.argv[1]:
    print_usage()
    sys.exit(1)

  try:
    header = open(sys.argv[1])
  except:
    print "error: HEADER file", sys.argv[1], "not found."
    print
    print_usage()
    sys.exit(1)

  try:
    footer = open(sys.argv[2])
  except:
    print "error: FOOTER file", sys.argv[2], "not found."
    print
    print_usage()
    sys.exit(1)

  try:
    template = open(sys.argv[3])
  except:
    print "error: TEMPLATE file", sys.argv[3], "not found."
    print
    print_usage()
    sys.exit(1)

  try:
    csv = open(sys.argv[4])
  except:
    print "error: CSV", sys.argv[4], "not found."
    print
    print_usage()
    sys.exit(1)

  p = Parser(header, footer, template, csv)

  out = p.parse();

  header.close()
  footer.close()
  template.close()
  csv.close()

  print out
