#!/usr/bin/env python
'''Application setup, build and infomation'''
import sys
import subprocess
from setuptools import setup, find_packages, Command
from templatizator.domain.helper import OS


class BuildExecutableCommand(Command):
    '''Build one executable file with pyinstaller'''

    description = 'Build one executable file with pyinstaller'
    user_options = []

    def initialize_options(self):
        '''Set default values to options'''
        pass

    def finalize_options(self):
        '''Post-process options'''
        pass

    def run(self):
        '''Run command'''
        command = [
            'pyinstaller',
            '--add-data=' +
            'templatizator/presentation/interface.ui;' +
            'templatizator/presentation',
            '--hidden-import=tkinter',
            '--onefile',
            '--noconsole',
            '--name=templatizator',
            '-y',
            '__main__.py',
        ]

        print(f'Running Command: {str(command)}')
        subprocess.call(command)

requirements = ['pygubu==0.9.8.2']

if OS.is_linux:
    requirements.append('ttkthemes==2.1.0')

dev_requirements = [
    'pyinstaller==3.4',
    'setuptools==40.6.3',
    'babel==2.6.0',
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Templatizator',
    version='1.0.0',
    description=\
        'Create sets of template files at software projects or some directory',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Jhonas Nascimento',
    author_email='jhonasn@gmail.com',
    url='https://github.com/jhonasn/templatizator',
    license='MIT',
    classifiers=[
        'Development Status :: 3 Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT Licence',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='project template configurable file DDD',
    platforms=[
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft',
        'Operating System :: Microsoft :: Windows',
    ],
    packages=find_packages(exclude=['doc', 'test']),
    install_requires=requirements,
    setup_requires=dev_requirements,
    package_data={
        'interface': ['presentation/interface.ui'],
    },
    cmdclass={ 'buildexecutable': BuildExecutableCommand }
)
