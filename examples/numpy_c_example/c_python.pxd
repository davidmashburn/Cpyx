# -*- Mode: Python -*-  Not really, but close enough

# Expose as much of the Python C API as we need here

cdef extern from "stdlib.h":
    ctypedef int size_t

cdef extern from "Python.h":
    ctypedef int Py_intptr_t