import Cpyx
import numpy as np

# It's magic ;)
exec(Cpyx.CythonInline('''
print 'Hello Cython!'
'''))

# And it supports numpy ;)
exec(Cpyx.CythonInline('''
import numpy as np
cimport numpy as np
def f(np.ndarray[np.int_t,ndim=1] a):
    cdef int i
    cdef int aLen = a.shape[0]
    for i in range(aLen):
        a[i]=a[i]*2
'''))
#''',useDistutils=True)) # replace above line with this to use distutils instead

arr = np.array([10,35,50],dtype=np.int)
f(arr)
print arr
