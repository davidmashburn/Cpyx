import Cpyx
Cpyx.cpyx('example', 'example_c', use_distutils=True)

import example

example.test(1, 2)
