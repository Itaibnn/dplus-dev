import os
import numpy
import shutil
import sys
from setuptools import setup
from distutils.extension import Extension
import setuptools
from setuptools.command.build_ext import build_ext as original_build_ext

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

with open(os.path.join(os.path.dirname(__file__), 'LICENSE.txt')) as license:
    LICENSE = license.read()

DEBUG = True # '--with-debug' in sys.argv
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))  # This is the project's root dir
API_DIR = os.path.dirname(__file__)
INCLUDE_DIRS = [ROOT_DIR, os.path.join(ROOT_DIR, 'Common')]
LIBRARY_DIRS = [os.path.join(ROOT_DIR, "x64", "ReleaseWithDebugInfo" if DEBUG else "Release")]
REQUIRED_DLLS = ['cudart64_110', 'curand64_10', 'lua51-backend', 'PDBReaderLib', 'xplusbackend']

extra_compile_args = []
extra_link_args = []
if sys.platform == 'win32':
    extra_compile_args = ['/Ox'] if not DEBUG else []
    LIBRARY_DIRS = [os.path.join(ROOT_DIR, "x64", "ReleaseWithDebugInfo" if DEBUG else "Release")]
    REQUIRED_DLLS = ['cudart64_110', 'curand64_10', 'lua51-backend', 'PDBReaderLib', 'xplusbackend']
    LIBRARIES = ['xplusbackend']
    DLL_SUFFIX = '.dll'
    DLL_PREFIX = ''
    # extra_link_args = ['/debug']
elif sys.platform in ['linux', 'linux2']:
    extra_compile_args = ['-fPIC', '-std=c++14']
    DLL_PREFIX = 'lib'
    DLL_SUFFIX = '.so'
    LIBRARY_DIRS = [os.path.join(API_DIR, 'lib')]
    LIBRARIES = ['backend']
    REQUIRED_DLLS = ['backend']

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

class PrepareCommand(setuptools.Command):
    description = "Convert the pyx files to cpp so there's no cython dependence in installation"
    # user_options = [('debug', None, 'debug')]
    user_options = []

    def initialize_options(self):
        # self.debug = None
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("running prepare command")
        first_pyx = os.path.join('dplus', 'wrappers', 'wrappers.pyx')
        self.convert_to_c(first_pyx)
        self.move_dlls()


    def convert_to_c(self, pyx):
        #creates fast.h and fast.c in cpp_wrapper folder
        print('Converting dplus pyx files to C++ sources...')
        print(pyx)
        self.cython(pyx)
        print('Converting {} pyx files to C++ sources...'.format(pyx.split("/")[-1]))


    def cython(self, pyx):
        from Cython.Compiler.CmdLine import parse_command_line
        from Cython.Compiler.Main import compile
        options, sources = parse_command_line(['-2', '-v', '--cplus', pyx])
        result = compile(sources, options)
        if result.num_errors > 0:
            print('Errors converting %s to C++' % pyx, file=sys.stderr)
            raise Exception('Errors converting %s to C++' % pyx)
        self.announce('Converted %s to C++' % pyx)

    def move_dlls(self):
        # Move DLLs (or shared objects) so they can be included in the package.
        print('Copying necessary DLLs')
        for dll in REQUIRED_DLLS:
            dll_filename = DLL_PREFIX + dll + DLL_SUFFIX
            shutil.copy(os.path.join(LIBRARY_DIRS[0], dll_filename), 'dplus')



setup(
    name='dplus-api',
    version='4.6',
    packages=['dplus'],
    package_data= { 'dplus': ['*.dll', '*.so' ]},
	install_requires=['numpy>=1.10', 'psutil>=5.6.3', 'requests>=2.10.0', 'pyceres>=0.1.0'],
    # include_package_data=True, # If True - ignores the package_data property.
    license=LICENSE,  # example license
    description='Call the DPlus Calculation Backend',
    url='https://scholars.huji.ac.il/uriraviv',
    author='Devora Witty',
    author_email='devorawitty@chelem.co.il',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
    cmdclass={
        'prepare': PrepareCommand,
    },
    ext_modules=[
        Extension(
            "dplus.wrappers",
            ["dplus/wrappers/wrappers.cpp"],
            language='c++',
            include_dirs=INCLUDE_DIRS + [numpy.get_include()],
            library_dirs=LIBRARY_DIRS,
            libraries=LIBRARIES,
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args),
    ]
)
