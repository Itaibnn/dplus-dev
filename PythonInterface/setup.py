import os
import numpy
import shutil
import sys
from setuptools import setup
from distutils.extension import Extension
import setuptools

INCLUDE_DIR = os.path.join('build', 'include')
COMMON_DIR = os.path.join(INCLUDE_DIR, "Common")

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

with open(os.path.join(os.path.dirname(__file__), 'LICENSE.txt')) as license:
    LICENSE = license.read()

extra_compile_args = []
extra_link_args = []
if sys.platform == 'win32':
    macros = [('GOOGLE_GLOG_DLL_DECL', '_CRT_SECURE_NO_WARNINGS'),
              ('CERES_USE_CXX_THREADS', None),
              ('_MBCS', None),
              ('CERES_USING_STATIC_LIBRARY', None)]
    extra_compile_args = ['/Ox']
    # extra_link_args = ['/debug']
elif sys.platform in ['linux', 'linux2']:
    extra_compile_args = ['-fPIC', '-std=c++14']
    macros = [('GOOGLE_GLOG_DLL_DECL', '_CRT_SECURE_NO_WARNINGS'),
              ('CERES_USE_CXX_THREADS', None),
              ('_MBCS', None),
              ('CERES_USING_STATIC_LIBRARY', None)]

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
class PrepareCommand(setuptools.Command):
    description = "Convert the pyx files to cpp so there's no cython dependence in installation"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("running prepare command")
        self.copy_source_files()
        first_pyx = './dplus/grid_wrap/CythonGrid.pyx'
        self.convert_to_c(first_pyx)

    def copy_source_files(self):
        if os.path.exists(INCLUDE_DIR):
            shutil.rmtree(INCLUDE_DIR)
        os.makedirs(INCLUDE_DIR)
        # create directories with the same hierarchy as dplus
        backend_dir = os.path.join(INCLUDE_DIR, "Backend", "Backend")
        os.makedirs(backend_dir)
        print("copying backend files")
        shutil.copy(r"../Backend/Backend/backend_exception.cpp", backend_dir)
        shutil.copy(r"../Backend/Backend/backend_exception.h", backend_dir)
        shutil.copy(r"../Backend/Backend/Grid.cpp", backend_dir)
        shutil.copy(r"../Backend/Backend/Grid.h", backend_dir)
        shutil.copy(r"../Backend/Backend/PeriodicSplineSolver.h", backend_dir)
        shutil.copy(r"./Residual.h", backend_dir)

        os.makedirs(COMMON_DIR)
        print("copying common files")
        shutil.copy(r"../Common/Common.h", COMMON_DIR)
        shutil.copytree(r"../Common/Eigen", os.path.join(COMMON_DIR, "Eigen"))
        shutil.copytree(r"../Common/rapidjson", os.path.join(COMMON_DIR, "rapidjson"))

        print("copying ziplib files")
        zip_lib_dir = os.path.join(COMMON_DIR, r"ZipLib/Source")
        os.makedirs(zip_lib_dir)
        shutil.copytree(r"../Common/ZipLib/Source/compression", os.path.join(zip_lib_dir, "compression"))
        shutil.copytree(r"../Common/ZipLib/Source/methods", os.path.join(zip_lib_dir, "methods"))
        shutil.copytree(r"../Common/ZipLib/Source/streams", os.path.join(zip_lib_dir, "streams"))
        shutil.copytree(r"../Common/ZipLib/Source/utils", os.path.join(zip_lib_dir, "utils"))
        shutil.copy(r"../Common/ZipLib/Source/ZipFile.h", zip_lib_dir)
        shutil.copy(r"../Common/ZipLib/Source/ZipArchive.h", zip_lib_dir)
        shutil.copy(r"../Common/ZipLib/Source/ZipArchiveEntry.h", zip_lib_dir)

        detail_dir = os.path.join(zip_lib_dir, r"detail")
        os.makedirs(detail_dir)
        shutil.copy(r"../Common/ZipLib/Source/detail/EndOfCentralDirectoryBlock.h", detail_dir)
        shutil.copy(r"../Common/ZipLib/Source/detail/ZipCentralDirectoryFileHeader.h", detail_dir)
        shutil.copy(r"../Common/ZipLib/Source/detail/ZipGenericExtraField.h", detail_dir)
        shutil.copy(r"../Common/ZipLib/Source/detail/ZipLocalFileHeader.h", detail_dir)

        zlib_dir = os.path.join(zip_lib_dir, r"extlibs/zlib")
        os.makedirs(zlib_dir)
        base_zlib_dir = r"../Common/ZipLib/Source/extlibs/zlib"
        files_list = os.listdir(base_zlib_dir)
        for filename in files_list:

            if os.path.splitext(filename)[1] != ".h":
                continue
            shutil.copy(os.path.join(base_zlib_dir, filename), zlib_dir)


        conversions_dir = os.path.join(INCLUDE_DIR, "Conversions")
        os.makedirs(conversions_dir)
        shutil.copy(r"../Conversions/JsonWriter.h", conversions_dir)

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

setup(
    name='dplus-api',
    version='4.4.1',
    packages=['dplus'],
	install_requires=['numpy>=1.10', 'psutil==5.6.3', 'requests>=2.10.0', 'pyceres>=0.1.0'],
    include_package_data=True,
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
            "CythonGrid",
            ["dplus/grid_wrap/CythonGrid.cpp"],
            language='c++',
            include_dirs=[INCLUDE_DIR, COMMON_DIR,
                          numpy.get_include()],
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args),
    ]
)
