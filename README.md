monkey
======

monkey is a simple utility that is used to translate a CSV table, using a
template file that defines the translation rules, a header file and a footer
file into (some sort of) output. The result is written to standard output.

sample usage
------------

The files for this example are available under the *sample* subfolder.

**header_file:**
    struct Foo
    {
    private:

**footer_file:**
    };

**template_file:**
    %1% %2%; 

**csv_file:**
    int,foo
    bool,bar


    $ monkey sample/header sample/footer sample/template sample/csv

    class Foo
    {
    private:
      int foo; 
      bool bar; 
    };

This is quite a small example of what monkey can be used for, but where it
really shines is when you e.g. perform a lot of similar operations on data types,
or need to generate both source and test code from data that can easily be
expressed in a tabular form (e.g. variables in a communication protocol).

template files
--------------

For each line of the CSV file, the template file is appended to the output
stream, with each occurence of %[0-9]+% (e.g. %1%) in the template stream
replaced with the corresponding item (items being separated by comma *,*) of the
current CSV row, where %1% represents the first item in the CSV row.

header and footer files
-----------------------

The header and footer files are appended and prepended, respectively, to the
output stream as-is.
