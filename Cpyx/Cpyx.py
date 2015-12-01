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
# gcc -shared numpyTest.c -IC:/Python25/include -LC:/Python25/libs -LC:/Users/me/Programming/Python/Pyx -lpython25 -lnumpyTestC -o numpyTest.pyd
#
# Author: David Mashburn
# Created July 2006
# Last Modified December 2015
# License: BSD or Apache 2


import os
import sys
from distutils.core import setup
from distutils.extension import Extension

import numpy
from Cython.Build import cythonize

# GLOBAL OPTIONS:
globalUseDistutils = False

# SYSTEM INFORMATION:
isWindows = (sys.platform=='win32')
isMac = (sys.platform=='darwin')
isLinux = (sys.platform=='linux2')

if not (isWindows or isMac or isLinux):
    print 'Platform "' + sys.platform + '" not supported yet'

verStr = '.'.join(map(str, sys.version_info[:2])) # recently, 2.6 or 2.7
verStr2 = ''.join(map(str, sys.version_info[:2])) # recently, 26 or 27

# Helper functions:
wrap = lambda s: '"' + s + '"'
rep = lambda s: s.replace('\\','\\\\')
join = os.path.join
jsys = lambda *args: join(sys.prefix, *args)

def usr_or_local(*args):
    x = jsys(*args)
    return x if os.path.exists(x) else jsys('local', *args)

# Full path to the Pyrex compiler script
pyrexcName = wrap(jsys('Scripts', 'pyrexc.py') if isWindows else
                  usr_or_local('bin', 'pyrexc'))
# Full path to the Cython compiler script
cythonName = wrap(jsys('Lib', 'site-packages', 'cython.py') if isWindows else
                  usr_or_local('bin', 'cython'))

# Full path to python executable
pythonName = (jsys('python.exe') if isWindows else
              usr_or_local('bin', 'python'))
#pythonName = sys.executable # Could probably just use this

# Python's include and Libs directories:
pythonInclude = usr_or_local('include', 'python' + (verStr if isLinux else ''))

pythonLibs = (jsys('libs') if isWindows else
              jsys('lib', 'python'+verStr,'config/') if isMac else
              jsys('lib'))

# Find numpy's arrayobject.h to include
arrayobjecthPath = os.path.join(numpy.get_include(),'numpy','arrayobject.h')
arrayObjectDir = numpy.get_include()

# Takes:
# 0 - name
# 1 - name of main pyx file (no extension)
# 2 - a comma-demimited list of quoted file names
# 3 - a comma-delimited list of compiler options
# 4 - number of threads

#'-Wno-unused-function', 
#'-stdlib=libc++',
#'-std=c++11', 
#'-mmacosx-version-min=10.8',

def _system(cmd, use_print=True):
    if type(cmd) is not str:
        cmd = ' '.join(cmd)
    
    if use_print:
        print '\n', cmd
    
    return os.system(cmd)

os.environ['MYPYREX'] = '/media/home/Programming/Python/Pyx/'

def ResolvePath(pth):
    '''Return the path if it is not an empty
    Otherwise try to use os.environ['MYPYREX']
    And fall back on the current directory'''
    return (pth if os.path.exists(pth) else
            os.environ['MYPYREX'] if 'MYPYREX' in os.environ else
            os.getcwd())

def Cdll(cNameIn='',printCmds=True, gccOptions=''):
    '''Use gcc to compile a shared library (.dll on Windows, .so on *nix)'''
    cwd = os.getcwd()
    
    cPath, cName = os.path.split(cNameIn) # input path and input file name
    dllPath = cPath = ResolvePath(cPath)
    
    stripName = os.path.splitext(cName)[0] # input file name without extension
    
    dllName = wrap(join(dllPath, (stripName+'.dll' if isWindows else
                                  'lib'+stripName+'.so')))
    
    cName = wrap(join(cPath, stripName+'.c')) # redefine cName
    hName = wrap(join(cPath, stripName+'.h'))
    oName = wrap(join(dllPath, stripName+'.o'))
    
    os.chdir(cPath)
    
    _system(['gcc', gccOptions, '-fPIC', '-c', cName, '-o', stripName+'.o'], printCmds)
    _system(['gcc', '-shared', '-o', dllName, oName], printCmds)
    
    os.chdir(cwd)

def Cpyx(pyxNameIn='CythonExample.pyx',useDistutils=globalUseDistutils,useCython=globalUseCython,gccOptions='',printCmds=True):
    '''Run Cython (or Pyrex) and then GCC to generate a Python extension module'''
    cwd = os.getcwd()
    
    pyxPath, pyxName = os.path.split(pyxNameIn) # input path and input file name
    
    pydPath = mainDir = ResolvePath(pyxPath)
    pyxStrip = os.path.splitext(pyxName)[0] # input file name without extension
    
    extName = wrap(pyxStrip)
    pyxName = wrap(join(mainDir, pyxStrip+'.pyx')) # Full path to the PYX file (must be in Python/Pyx folder) redefine pyxName
    pyx2cName = wrap(join(pydPath, pyxStrip+'.c')) # Full path to the C file to be created
    pydName = wrap(join(pydPath, pyxStrip+'.pyd')) # Full path to the PYD file to be created
    soName = wrap(join(pydPath, pyxStrip+'.so')) # Full path to the lib*.so file to be created
    setupName = wrap(join(pydPath, 'setup.py')) # Full path of the Setup File to be created
    
    if useDistutils:
        '''
        output_name = 
        main_pyx_name = 
        source_files = 
        nthreads = 4
        extra_compile_args=[]
        extensions = [Extension(main_pyx_name, [source_files], extra_compile_args=extra_compile_args)]
        setup(name=name, ext_modules=cythonize(extensions, nthreads=nthreads))
        
        extensions = [Extension(output_name, source_files,
                      include_dirs = ['.'],
              extra_compile_args=cargs)]

setup(ext_modules=cythonize(extensions, nthreads=nthreads),
      #script_args = ['build_ext', '--build-lib='+d, '--build-temp=/tmp/'])
      script_args = ['build_ext', '--inplace'])
        
        #write setup.py which will make a PYD file that can be imported
        setupText = 

        
        if printCmds:
            print 'Write Stuff to ', setupName[1:-1]
        fid = open(setupName[1:-1],'w') # [1:-1] removes quotes
        fid.write(setupText)
        fid.close()
        
        # run setup.py
        
        os.chdir(mainDir)
        
        if sys.platform=='win32':        cmd=' '.join([pythonName,setupName,'build_ext','--compiler=mingw32','--inplace'])
        elif sys.platform=='darwin':     cmd=' '.join([pythonName,setupName,'build_ext','--inplace'])
        elif sys.platform=='linux2':     cmd=' '.join([pythonName,setupName,'build_ext','--inplace'])
        else:                            print 'Platform "' + sys.platform + '" not supported yet'
        '''
    else:
        # run the main pyrex command to make the C file
        pyxCompiler = cythonName if useCython else pyrexcName
        _system([pythonName,pyxCompiler,pyxName,'-o',pyx2cName])
        
        cmds = (['gcc', gccOptions, '-fPIC', '-shared', pyx2cName, '-I'+pythonInclude, '-I'+arrayObjectDir, '-L'+pythonLibs, '-lpython'+verStr2, '-o', pydName]
                if isWindows else
                ['gcc', gccOptions, '-fno-strict-aliasing', '-Wno-long-double', '-no-cpp-precomp', '-mno-fused-madd', '-fno-common',
                 '-dynamic', '-DNDEBUG', '-g', '-O3', '-bundle', '-undefined dynamic_lookup', '-I'+pythonInclude,
                 '-I'+pythonInclude+'/python'+verStr, '-I'+arrayObjectDir, '-L'+pythonLibs, '-L/usr/local/lib', pyx2cName, '-o', soName]
                if isMac else
                ['gcc', gccOptions, '-fPIC', '-shared', pyx2cName, '-I'+pythonInclude, '-L'+pythonLibs, '-lpython'+verStr, '-o', soName]
               )
    
    _system(cmds)
    
    os.chdir(cwd)

def CpyxLib(pyxNameIn='CythonExample.pyx',cNameIn='CTestC.c',recompile=True,useDistutils=globalUseDistutils,useCython=globalUseCython,gccOptions='',printCmds=True):
    '''Compile a C source and then run Cython/GCC on a pyx file, linking the C source
    Alternatively, use Cython.Distutils to do the same thing'''
    cwd=os.getcwd()
    
    pyxPath, pyxName = os.path.split(pyxNameIn) # input path and input file name
    cPath, cName = os.path.split(cNameIn) # input path and input file name
    
    pydPath = mainDir = ResolvePath(pyxPath)
    dllPath = cPath = ResolvePath(cPath)
    
    pyxStrip = os.path.splitext(pyxName)[0] # input file name without extension
    cStrip = os.path.splitext(cName)[0] # input file name without extension
    
    extName = wrap(pyxStrip)
    pyxName = wrap(join(mainDir, pyxStrip+'.pyx')) # Full path to the PYX file (must be in Python\\Pyrex folder)
    
    dllName = wrap(join(dllPath, (cStrip+'.dll' if isWindows else
                                  'lib'+cStrip+'.so')))
    
    libName = wrap(join(dllPath,cStrip) if isWindows else
                   cStrip)
    
    lib_template = '''
    library_dirs=[{0}],
    runtime_library_dirs=[{0}],'''
    
    library_dirs_txt = ('' if isWindows else
                        lib_template.format(rep(pydPath)))
    
    cName = wrap(join(cPath,cStrip+'.c'))
    hName = wrap(join(cPath,cStrip+'.h'))
    oName = wrap(join(dllPath,cStrip+'.o'))
    
    os.chdir(cPath)
    
    pyx2cName = wrap(join(pydPath, pyxStrip+'.c')) # Full path to the C file to be created
    setupName = wrap(join(pydPath, 'setup.py')) # Full path of the Setup File to be created
    pydName = wrap(join(pydPath, pyxStrip+'.pyd')) # Full path to the PYD file to be created
    soName = wrap(join(pydPath, pyxStrip+'.so')) # Full path to the lib*.so file to be created
    
    if useDistutils:
        #write setup.py which will make a PYD file that can be imported
        setup_template = """"""
        if printCmds:
            print 'Write Stuff to ', setupName[1:-1]
        fid = open(setupName[1:-1],'w') # [1:-1] removes quotes
        fid.write(setupText)
        fid.close()
        
        # run setup.py
        os.chdir(mainDir)
        
        _system([pythonName, setupName, 'build_ext', ('--compiler=mingw32' if isWindows else ''), '--inplace'])
    else:
        # compile the DLL needed for the link to the C file
        if recompile:
            Cdll(cName[1:-1], printCmds=printCmds, gccOptions=gccOptions) # [1:-1] to remove the quotes
        
        # run the main pyrex command to make the C file
        pyxCompiler = cythonName if useCython else pyrexcName
        _system([pythonName, pyxCompiler, pyxName, '-o', pyx2cName])
        
        _system(['gcc', gccOptions, '-fPIC', '-shared', pyx2cName, '-I'+pythonInclude, '-L'+pythonLibs, '-L'+cPath, '-Wl,-R'+cPath,
                        '-lpython'+verStr2, '-l'+cStrip, '-o', pydName]
                if isWindows else
                ['gcc', gccOptions, '-fno-strict-aliasing', '-Wno-long-double', '-no-cpp-precomp', '-mno-fused-madd', '-fno-common',
                        '-dynamic', '-DNDEBUG', '-g', '-O3', '-bundle', '-undefined dynamic_lookup', '-I'+pythonInclude,
                        '-I'+pythonInclude+'/python'+verStr, '-I'+arrayObjectDir, '-L'+pythonLibs, '-L/usr/local/lib', '-L'+cPath, '-Wl,-R'+cPath,
                        '-l'+cStrip, pyx2cName, '-o', soName]
                if isMac else
                ['gcc', gccOptions, '-fPIC', '-shared', pyx2cName, '-I'+pythonInclude, '-L'+pythonLibs, '-L'+cPath, '-Wl,-R'+cPath,
                        '-lpython'+verStr, '-l'+cStrip, '-o', soName])
    
    os.chdir(cwd)

