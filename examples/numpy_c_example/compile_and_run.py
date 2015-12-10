import Cpyx
Cpyx.cpyx('numpy_example', 'numpy_example_c', use_distutils=True)

import numpy_example

numpy_example.numpy_test()

