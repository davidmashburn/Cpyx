import Cpyx

# It's magic ;)
exec(Cpyx.CythonInline('''
print 'Hello Cython!'
'''))
