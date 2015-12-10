cimport c_python
cimport c_numpy
import numpy as np

ctypedef c_numpy.ndarray cn

cdef extern from "numpy_example_c.h":
    int SampleInt
    int something(int i, int j)
    struct Cstruct:
        int cat
        int dog
    int numpy_float_test(float * f, int size)

def numpy_test():
    arr = np.array([1, 2, 3, 4, 5], np.float32)
    
    for i in arr:
        print 'arr: ',i
    
    cdef cn arr_cn
    arr_cn = arr
    
    cdef float * f
    f = <float *> arr_cn.data
    
    return numpy_float_test(f, arr.size)
