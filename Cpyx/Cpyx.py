# Automatically compile Cython code
# - Can generate compiler commands (with gcc) or use distutils
# - Supports building included C modules as well
# - Numpy support automatically enabled
# - By default, outputs system commands to aid debugging
#
# Previously tested on Windows, Mac, and Ubuntu Linux
# (but use at you're own peril)
# My main goal is to help others learn how to compile cython code
# on various systems so they can tweak it to suit their needs
# Pyrex support has now been dropped
#
# Getting gcc:
# Windows: Download the latest mingw and
#          add "C:\MinGW\bin" to the PATH environment variable
#
# Mac:     Download Xcode from Apple and install it:
#
# Linux:   Get the build tools for your platform that include gcc
#          (build-essentials on Debian/Ubuntu)
#
# Old, out of date sample outputs from Cpyx on Windows with Python2.5:
# Pieces:
# gcc -c -IC:/Python25/include PyrexExample.c -o PyrexExample.o
# gcc -shared PyrexExample.o -LC:/Python25/libs -lpython25 -o PyrexExample.pyd
#
# All-in-one:
# gcc -shared PyrexExample.c -IC:/Python25/include -LC:/Python25/libs -lpython25 -o PyrexExample.pyd
#
# All-in-one with linking dll...
# gcc numpyTest.c -shared -IC:/Python25/include -LC:/Python25/libs -LC:/Users/me/Programming/Python/Pyx -lpython25 -lnumpyTestC -o numpyTest.pyd
#
# Author: David Mashburn
# Created July 2006
# Last Modified December 2015
# License: BSD or Apache 2


import os
import sys
import types
import random
import multiprocessing
from distutils.core import setup
from distutils.extension import Extension

import numpy
from Cython.Build import cythonize

# GLOBAL OPTIONS:
USE_DISTUTILS = True
PRINT_CMDS = True

# SYSTEM INFORMATION:
isWindows = (sys.platform=='win32')
isMac = (sys.platform=='darwin')
isLinux = (sys.platform=='linux2')

if not (isWindows or isMac or isLinux):
    print 'Platform "' + sys.platform + '" not supported yet'

# 2.7 on *nix, 27 on Windows
VERSION_STR = ('' if isWindows else '.').join(map(str, sys.version_info[:2]))

# Helper functions:
quote = lambda s: '"' + s + '"'
jsys = lambda *args: os.path.join(sys.prefix, *args)

def usr_or_local(*args):
    x = jsys(*args)
    return x if os.path.exists(x) else jsys('local', *args)

# Full path to the Pyrex compiler script
#PYREX = quote(jsys('Scripts', 'pyrexc.py') if isWindows else
#             usr_or_local('bin', 'pyrexc'))

# Full path to the Cython compiler script
CYTHON = quote(jsys('Lib', 'site-packages', 'cython.py') if isWindows else
              usr_or_local('bin', 'cython'))

# Full path to python executable
PYTHON = (jsys('python.exe') if isWindows else
          usr_or_local('bin', 'python'))
#PYTHON = sys.executable # Could probably just use this

# Python's include and Libs directories:
PYTHON_INCLUDE = usr_or_local('include', 'python' + (VERSION_STR if isLinux else ''))

PYTHON_LIBS = (jsys('libs') if isWindows else
               jsys('lib', 'python'+VERSION_STR,'config/') if isMac else
               jsys('lib'))

# Find numpy's arrayobject.h to include
ARRAY_OBJECT_H = os.path.join(numpy.get_include(),'numpy','arrayobject.h')
ARRAY_OBJECT_DIR = numpy.get_include()

# Takes:
# 0 - name
# 1 - name of main pyx file (no extension)
# 2 - a comma-demimited list of quoted file names
# 3 - a comma-delimited list of compiler options
# 4 - number of threads

def islistlike(x):
    '''Test if something is an iterable but NOT as string'''
    return hasattr(x, '__iter__') and not isinstance(x, types.StringTypes)

def _listify(x, n=1):
    '''Wrap x as a list if it is not already a list.
       Optionally duplicate the value n times'''
    return x if islistlike(x) else [x]*n

def _system(command, directory=None, use_print=True):
    if type(command) is not str:
        command = ' '.join(command)
    
    if use_print:
        print ''
        print command
    
    if directory is not None:
        cwd = os.getcwd()
        os.chdir(directory)
    
    out = os.system(command)
    
    if directory is not None:
        os.chdir(cwd)
    
    return out

def _resolve_path(pth):
    '''Return the path if it is not an empty
       and fall back on the current directory'''
    rel = os.path.join(os.getcwd(), pth) # in case path is relative
    return (pth if os.path.exists(pth) else
            rel if os.path.exists(rel) else
            os.getcwd())

def split_with_ext(filename):
    path, name = os.path.split(filename)
    base_name, ext = os.path.splitext(name)
    path = _resolve_path(path)
    return path, base_name, ext

def build_path(path, base_name, ext, use_quote=False):
    '''Build a quoted path'''
    p = os.path.join(path, base_name+ext)
    return quote(p) if use_quote else p

def build_path_list(paths, base_names, exts, use_quote=False):
    '''Build a list of quoted paths
       "paths" and "exts" can optionally be common values instead of lists'''
    paths = _listify(paths, n=len(base_names))
    exts = _listify(exts, n=len(base_names))
    return [build_path(p, b, e, use_quote)
            for p, b, e in zip(paths, base_names, exts)]

def cc(c_filenames_in, output_path=None, gcc_options=None,
       ld_options=None, print_cmds=PRINT_CMDS):
    '''Call gcc to compile a shared library
       (.dll on Windows, lib*.so on *nix)
       Places output next to first c file unless otherwise specified'''
    gcc_options = ['-fPIC'] if gcc_options is None else list(gcc_options)
    ld_options = ([] if ld_options is None else
                  ['-Wl,'+i for I in ld_options])
    
    c_filenames_in = _listify(c_filenames_in)
    
    paths, base_names, _ = zip(*map(split_with_ext, c_filenames_in))
    main_name = base_names[0]
    lib_name = main_name+'.dll' if isWindows else 'lib'+main_name+'.so'
    
    output_path = (paths[0] if output_path is None else
                   _resolve_path(output_path))
    
    c_files = build_path_list(paths, base_names, '.c', use_quote=True)
    o_files = build_path_list(output_path, base_names, '.o', use_quote=True)
    lib_file = quote(os.path.join(output_path, lib_name))
    
    # Compile each object file
    for c_file, o_file in zip(c_files, o_files):
        _system(['gcc'] + gcc_options + ['-c', c_file, '-o', o_file],
                output_path, print_cmds)
    
    # Combine into a shared library
    _system(['gcc', '-shared'] + ld_options + ['-o', lib_file] + o_files,
            output_path, print_cmds)

def _has3(x):
    '''Return x unless x is an empty list; in that case return 3 empty lists'''
    return ([],[],[]) if x == [] else x


def cpyx(pyx_filenames_in, c_filenames_in=(), output_path=None,
         gcc_options=None, ld_options=None, use_distutils=USE_DISTUTILS,
         nthreads=None, recompile=True, print_cmds=PRINT_CMDS):
    '''Run Cython and then GCC to generate a Python extension module
       Optionally include c files to build and link in as well
       Now uses distutils by default'''
    pyx_filenames_in, c_filenames_in = map(_listify, [pyx_filenames_in, c_filenames_in])
    
    pyx_paths, pyx_base_names, _ = zip(*map(split_with_ext, pyx_filenames_in))
    c_paths, c_base_names, _ = _has3(zip(*map(split_with_ext, c_filenames_in)))
    main_name = pyx_base_names[0] # use the first cython name as the project name
    c_shared_lib_name = c_base_names[0] if c_base_names else '' # use the first c name as the shared library name that we link to
    lib_name = main_name + ('.pyd' if isWindows else '.so')
    
    output_path = (pyx_paths[0] if output_path is None else
                   _resolve_path(output_path))
    
    pyx_files = build_path_list(pyx_paths, pyx_base_names, '.pyx')
    c_files = build_path_list(c_paths, c_base_names, '.c')
    pyx_c_files = build_path_list(pyx_paths, pyx_base_names, '.c')
    lib_file = os.path.join(output_path, lib_name)
    
    if use_distutils:
        nthreads = multiprocessing.cpu_count() if nthreads is None else nthreads
        extra_compile_args = [] if gcc_options is None else gcc_options
        extra_link_args = [] if ld_options is None else ld_options
        
        cwd = os.getcwd()
        os.chdir(output_path)
        
        extensions = [Extension(main_name, pyx_files + c_files,
                                include_dirs=['.'],
                                extra_compile_args=extra_compile_args,
                                extra_link_args=extra_link_args)]
        setup(name=main_name,
              ext_modules=cythonize(extensions, nthreads=nthreads),
              script_args=['build_ext', '--inplace'])
        
        os.chdir(cwd)
        
        if print_cmds:
            'Build everything using distutils'
    else:
        # Optionally build a shared library from all the c files
        if recompile:
            cc(c_files, output_path, gcc_options, ld_options, print_cmds)
        
        # Quote the files
        pyx_files = map(quote, pyx_files)
        c_files = map(quote, c_files)
        pyx_c_files = map(quote, pyx_c_files)
        lib_file = quote(lib_file)
        
        # Run cython all the pyx files
        for pyx, c in zip(pyx_files, pyx_c_files):
            _system([PYTHON, CYTHON, pyx, '-o', c])
        
        # Build the big gcc command to combine everything
        cmd = ['gcc'] + pyx_c_files
        
        if gcc_options is not None:
            cmd += gcc_options
        
        if ld_options is not None:
            cmd += ['-Wl,'+i for i in ld_options]
        
        if isWindows:
            cmd += ['-fPIC', '-shared', '-I'+PYTHON_INCLUDE, '-I'+ARRAY_OBJECT_DIR, '-L'+PYTHON_LIBS, '-L'+cPath, '-Wl,-R'+cPath, '-lpython'+VERSION_STR]
        elif isMac:
            cmd += ['-fno-strict-aliasing', '-Wno-long-double', '-no-cpp-precomp', '-mno-fused-madd', '-fno-common',
                    '-dynamic', '-DNDEBUG', '-g', '-O3', '-bundle', '-undefined dynamic_lookup', '-I'+PYTHON_INCLUDE,
                    '-I'+PYTHON_INCLUDE+'/python'+VERSION_STR, '-I'+ARRAY_OBJECT_DIR, '-L'+PYTHON_LIBS, '-L/usr/local/lib']
        else:
            cmd += ['-fPIC', '-shared', '-I'+PYTHON_INCLUDE, '-L'+PYTHON_LIBS, '-lpython'+VERSION_STR]
        
        if c_filenames_in:
            # Link to the paths where the headers are and also to the location of the shared library built earlier
            cmd += ['-L'+c for c in c_paths]     # link to all the paths
            cmd += ['-Wl,-R'+c for c in c_paths] # link to all the paths (send to linker)
            cmd += ['-l'+c_shared_lib_name] # link to the shared library directly
        
        cmd += ['-o', lib_file]
        
        _system(cmd, directory=output_path)

TMP = os.path.expanduser('~/.Cpyx_inline_tmp/')

def cpyx_inline(code, tmp_dir=TMP, **kwds):
    '''Cython function for inline usage
       Write a temp .pyx file, compile, import, and return the module
       Differs from cython.inline in that more features are working ;)
       
       All keywords are passed to cpyx
       
       You may want to occasionally clear the cached files this generates:
       rm ~/.cpyx_inline_tmp/*
       '''
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    sys.path.append(tmp_dir)
    
    mn = 'out' + str(random.randint(0, 1e18))
    fn = os.path.join(tmp_dir, mn + '.pyx')
    with open(fn, 'w') as fid:
        fid.write(code)
    cpyx(fn, **kwds)
    exec('import ' + mn)
    exec('imported_module = ' + mn)
    
    sys.path.pop()
    
    return imported_module

## Other Helper Functions (useful for generating pxd files or filling in templates in pyx files, etc):

def get_function_raw_arguments(s, sig):
    '''For a C function, get all arguments as a single string
       (everything inside the parentheses):
          s is a filename (string)
          sig is something like "void foo"
       The function body must use {}'s for this to work.'''
    return s.split(sig)[1].split('{')[0].strip()[1:-1].strip()

def get_function_args(s, sig):
    '''For a C function, get a string for each argument'''
    return [i.strip() for i in get_function_raw_arguments(s, sig).split(',')]

def get_function_types_and_variables(s, sig):
    '''For a C function, get a list of [type, variable] for each argument'''
    most_and_last = lambda x: [' '.join(x[:-1]), x[-1]] # clump all arguments but the first one together
    return [most_and_last(i.replace('*', '* ').split())
            for i in get_function_args(s, sig)]

def rebuild_function_signature(s, sig):
    '''Recontruct the full function signature using "get_function_args".
       Whitespace is set to automatically to align all arguments.'''
    args = get_function_args(s, sig)
    return sig + '(' + (',\n' + ' '*(len(sig)+1)).join(args) + ')'


# Other GCC options that might be useful:
#'-Wno-unused-function', 
#'-stdlib=libc++',
#'-std=c++11', 
#'-mmacosx-version-min=10.8',
