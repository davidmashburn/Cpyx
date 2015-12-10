cdef extern from "example_c.h":
    int SampleInt
    int something(int i, int j)
    struct Cstruct:
        int cat
        int dog

def test(i, j):
    cdef int x
    cdef int y
    cdef Cstruct CS
    
    x=i
    y=j
    
    print SampleInt
    
    return something(x,y)
