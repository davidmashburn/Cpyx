# :Author:    Robert Kern
# :Copyright: 2004, Enthought, Inc.
# :License:   BSD Style

import sys
cimport c_python

cdef extern from "/usr/lib/python2.7/dist-packages/numpy/core/include/numpy/arrayobject.h":
    ctypedef class numpy.ndarray [object PyArrayObject]:
        cdef char *data
        cdef int nd
        cdef c_python.Py_intptr_t *dimensions
        cdef c_python.Py_intptr_t *strides
        cdef object base
        # descr not implemented yet here...
        cdef int flags
        cdef int itemsize
        cdef object weakreflist

    cdef void import_array()
