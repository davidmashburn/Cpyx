Cpyx is a utility script to automatically build C and Cython code using either distutils or command line cython and gcc. Numpy is supported in both cases.

The two core functions are cc and cpyx which compile c sources and cython+c sources respecively.

* "cc" builds a shared library from all included inputs, using path resolution and quoting to aid in debugging issues (gcc commands should run verbatim from any directory).

* "cpyx" builds multiple c and cython sources into a python extension module.
If use_distutils is True, compiles a monolithic module from all c and pyx sources.
If use_distutils is False, this first uses "cc" to compile a shared library from the given c sources, next uses cython to generate c files from all given pyx files, and then uses gcc to compile the resulting c sources into an extension module that links to the shared library. This is more complicated, but often easier to debug.

As noted, when not using distutils, "cpyx" makes direct system calls to Cython and gcc with switches for the 3 different major OS's (Windows, Linux, Mac).
Some aspects of these paths are hard-coded, so you may have problems if cython or gcc (or libpython) is in a non-standard place.
If this happens and Cpyx fails, you can either place a link to the real file in the spot Cpyx was looking for it in or just go into Cpyx.py and edit the paths at the top to match yours (just make sure you are looking at the right OS).

Cpyx is quite verbose, outputting each command in sequence, so you can easily copy and manually run/modify the compiler commands in the shell (and/or change the options inside Cpyx.py).
This way even if Cpyx doesn't quite work, maybe you can use it to help you learn how to use cython and gcc ;-)
Cpyx is quite simple (the main two functions are only ~100 lines of code), so it is easy to fiddle with.


NEW IN VERSION 0.2:
*All functions were significantly overhauled and function names were changed* (old Cdll and Cpyx/CpyxLib became "cc" and "cpyx" respectively).
Support for inlined cython code has been dropped since cython now supports this automatically using "cython.inline".

New helpful utilities for extracting C function information (i.e. to generate code using templates):
 * get_function_raw_arguments -- Get all arguments as a single string (everything inside the parentheses)
 * get_function_args -- Get a string for each argument
 * get_function_types_and_variables -- Get a list of [type, variable] for each argument
 * rebuild_function_signature -- Get a well-formatted version of the full function signature


Ideally, Cpyx should work anywhere gcc, cython, and python/numpy are installed.
The 0.1 branch was relatively well-tested and worked on Windows (XP/Vista/7), Linux (Ubuntu), and Mac OS X (Leopard/Snow Leopard). The 0.2 branch has been pretty thoroughly tested on Ubuntu Linux, but let me know if it does not work for you on any OS.
distutils may or may not work on Windows with mingw

I know there are other tools out there (most notably pyximport and sage's misc/cython.py) to do this same kind of thing (and in much cooler ways).
But Cpyx scratches my itch, so I thought I'd put it out there. Happy Cythoning!
