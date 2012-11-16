monkey development
==================

Notes
-----
This development setup guide uses virtualenv(http://www.virtualenv.org/en/latest/index.html)
and pip(http://pypi.python.org/pypi/pip).

Dependencies
------------
    $ pip freeze
    mox==0.5.3
    wsgiref==0.1.2

Setting up environment
----------------------
    $ virtualenv monkey
    $ cd monkey
    $ source bin/activate

    $ pip install mox

    $ git clone https://github.com/nthorne/monkey
