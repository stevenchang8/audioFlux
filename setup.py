#!/usr/bin/env python
import os
import sys
from sys import platform
from setuptools import find_packages, setup
import setuptools.command.build_py
# test

class BuildPyCommand(setuptools.command.build_py.build_py):

    def run(self):
        if sys.argv[1].startswith('build'):
            if platform.startswith('win'):
                raise ValueError('Platform=%s is not supported. Please use macOS to build the package. '
                                 'Or use `pip install audioflux` to install the package.' % platform)

            if sys.argv[1] == 'build_py_win':
                self.compile_c_win()
            else:
                is_whl = sys.argv[1] == 'build_py_whl'
                self.compile_c(is_whl=is_whl)
        setuptools.command.build_py.build_py.run(self)

    def compile_c(self, is_whl=False):
        """Only supports macOS/linux"""
        print('=' * 20)
        print('Starting compile audioFlux of c')
        if is_whl:
            os.environ['AF_BUILD_PY_BDIST'] = '1'
        current_cwd = os.getcwd()
        os.chdir(os.path.join(os.getcwd(), './scripts'))
        if platform == 'darwin':
            r = os.system('bash ./build_macOS.sh')
            filename = 'libaudioflux.dylib'
            src_lib_fp = './build/macOSBuild/{}'.format(filename)
        elif platform == 'linux':
            r = os.system('bash ./build_linux.sh')
            filename = 'libaudioflux.so'
            src_lib_fp = './build/linuxBuild/{}'.format(filename)
        else:
            raise ValueError('Platform={} is not supported'.format(platform))
        if r != 0:
            exit(-1)
        os.chdir(current_cwd)
        if is_whl:
            if platform == 'darwin':
                os.system("install_name_tool -change @rpath/libomp.dylib @loader_path/lib/libomp.dylib %s" % src_lib_fp)
            elif platform == 'linux':
                os.system("patchelf --set-rpath '$ORIGIN/lib' %s" % src_lib_fp)
        print('Compile audioFlux successful.')

        import shutil
        dst_lib_path = 'python/audioflux/lib'
        if not os.path.exists(dst_lib_path):
            os.makedirs(dst_lib_path)

        dst_lib_fp = os.path.join(dst_lib_path, filename)
        if os.path.exists(dst_lib_fp):
            os.remove(dst_lib_fp)
        shutil.copyfile(src_lib_fp, dst_lib_fp)
        print('Copying {src_lib_fp} to {dst_lib_fp}'.format(src_lib_fp=src_lib_fp, dst_lib_fp=dst_lib_fp))
        print('=' * 20)

    def compile_c_win(self):
        """Only supports macOS"""
        print('Starting compile audioFlux of c')
        current_cwd = os.getcwd()
        os.chdir(os.path.join(os.getcwd(), './scripts'))
        if platform == 'darwin' or platform == 'linux':
            r = os.system('bash ./build_windows.sh')
            filename = 'libaudioflux.dll'
            src_lib_fp = './build/windowBuild/libaudioflux.so'.format(filename)
        else:
            raise ValueError('Platform={} is not supported'.format(platform))
        if r != 0:
            exit(-1)
        os.chdir(current_cwd)
        print('Compile audioFlux successful.')

        import shutil
        dst_lib_path = 'python/audioflux/lib'
        if not os.path.exists(dst_lib_path):
            os.makedirs(dst_lib_path)

        dst_lib_fp = os.path.join(dst_lib_path, filename)
        if os.path.exists(dst_lib_fp):
            os.remove(dst_lib_fp)
        shutil.copyfile(src_lib_fp, dst_lib_fp)
        print('Copying {src_lib_fp} to {dst_lib_fp}'.format(src_lib_fp=src_lib_fp, dst_lib_fp=dst_lib_fp))
        print('=' * 20)


about = {}
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "python", "audioflux", "__version__.py"), "r") as f:
    exec(f.read(), about)

with open("README.md", "r") as f:
    readme = f.read()


def get_package_data():
    package_data = {
        'audioflux': ["utils/sample_data/*.wav"]
    }

    if sys.argv[1].startswith(('bdist', 'sdist')):
        package_data['audioflux'].extend(["lib/lib/*", "lib/*"])
    else:
        cur_sys = platform
        if sys.argv[1] == 'build_py_win':
            cur_sys = 'win32'

        if cur_sys == 'linux':
            package_data['audioflux'].extend(["lib/*.so"])
        elif cur_sys == 'darwin':
            package_data['audioflux'].extend(["lib/*.dylib"])
        elif cur_sys == 'win32':
            package_data['audioflux'].extend(["lib/*.dll"])

    return package_data


setup(
    name=about['__title__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords=[about['__title__']],
    version=about['__version__'],
    package_dir={"": "python"},
    packages=find_packages("python"),
    package_data=get_package_data(),
    author="audioflux",
    url='https://audioflux.top',
    project_urls={
        "Source": "https://github.com/libAudioFlux/audioFlux",
    },
    license='MIT',
    python_requires=">=3.6",
    install_requires=[
        "numpy",
        "scipy >= 1.2.0",
        "soundfile>=0.12.1",
        "matplotlib",
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Framework :: Matplotlib',
        'Programming Language :: C',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    cmdclass={
        'build_py': BuildPyCommand,
        'build_py_whl': BuildPyCommand,
        'build_py_win': BuildPyCommand,
    }
)
