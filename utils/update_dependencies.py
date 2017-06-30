#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to update the dependencies in various configuration files."""

from __future__ import unicode_literals
import os
import sys

# Change PYTHONPATH to include dependencies and projects.
sys.path.insert(0, '.')

import utils.dependencies  # pylint: disable=wrong-import-position
import utils.projects  # pylint: disable=wrong-import-position


# pylint: disable=redefined-outer-name


class DependencyFileWriter(object):
  """Dependency file writer."""

  def __init__(self, project_definition, dependency_helper):
    """Initializes a dependency file writer.

    Args:
      project_definition (ProjectDefinition): project definition.
      dependency_helper (DependencyHelper): dependency helper.
    """
    super(DependencyFileWriter, self).__init__()
    self._dependency_helper = dependency_helper
    self._project_definition = project_definition


class AppveyorYmlWriter(DependencyFileWriter):
  """Appveyor.yml file writer."""

  _PATH = os.path.join('appveyor.yml')

  _VERSION_PYWIN32 = '220'
  _VERSION_WMI = '1.4.9'

  _DOWNLOAD_PIP = (
      '  - ps: (new-object net.webclient).DownloadFile('
      '\'https://bootstrap.pypa.io/get-pip.py\', '
      '\'C:\\Projects\\get-pip.py\')')

  _DOWNLOAD_PYWIN32 = (
      '  - ps: (new-object net.webclient).DownloadFile('
      '\'https://github.com/log2timeline/l2tbinaries/raw/master/win32/'
      'pywin32-{0:s}.win32-py2.7.exe\', '
      '\'C:\\Projects\\pywin32-{0:s}.win32-py2.7.exe\')').format(
          _VERSION_PYWIN32)

  _DOWNLOAD_WMI = (
      '  - ps: (new-object net.webclient).DownloadFile('
      '\'https://github.com/log2timeline/l2tbinaries/raw/master/win32/'
      'WMI-{0:s}.win32.exe\', \'C:\\Projects\\WMI-{0:s}.win32.exe\')').format(
          _VERSION_WMI)

  _INSTALL_PIP = (
      '  - cmd: "%PYTHON%\\\\python.exe C:\\\\Projects\\\\get-pip.py"')

  _INSTALL_PYWIN32 = (
      '  - cmd: "%PYTHON%\\\\Scripts\\\\easy_install.exe '
      'C:\\\\Projects\\\\pywin32-{0:s}.win32-py2.7.exe"').format(
          _VERSION_PYWIN32)

  _INSTALL_WMI = (
      '  - cmd: "%PYTHON%\\\\Scripts\\\\easy_install.exe '
      'C:\\\\Projects\\\\WMI-{0:s}.win32.exe"').format(_VERSION_WMI)

  _DOWNLOAD_L2TDEVTOOLS = (
      '  - cmd: git clone https://github.com/log2timeline/l2tdevtools.git && '
      'move l2tdevtools ..\\')

  _FILE_HEADER = [
      'environment:',
      '  matrix:',
      '    - PYTHON: "C:\\\\Python27"',
      '',
      'install:',
      ('  - cmd: \'"C:\\Program Files\\Microsoft SDKs\\Windows\\v7.1\\Bin\\'
       'SetEnv.cmd" /x86 /release\''),
      _DOWNLOAD_PIP,
      _DOWNLOAD_PYWIN32,
      _DOWNLOAD_WMI,
      _INSTALL_PIP,
      _INSTALL_PYWIN32,
      _INSTALL_WMI,
      _DOWNLOAD_L2TDEVTOOLS]

  _L2TDEVTOOLS_UPDATE = (
      '  - cmd: mkdir dependencies && set PYTHONPATH=..\\l2tdevtools && '
      '"%PYTHON%\\\\python.exe" ..\\l2tdevtools\\tools\\update.py '
      '--download-directory dependencies --machine-type x86 '
      '--msi-targetdir "%PYTHON%" {0:s}')

  _FILE_FOOTER = [
      '',
      'build: off',
      '',
      'test_script:',
      '  - "%PYTHON%\\\\python.exe run_tests.py"',
      '']

  def Write(self):
    """Writes an appveyor.yml file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = self._dependency_helper.GetL2TBinaries()
    dependencies.extend(['funcsigs', 'mock', 'pbr', 'six'])
    dependencies = ' '.join(dependencies)

    l2tdevtools_update = self._L2TDEVTOOLS_UPDATE.format(dependencies)
    file_content.append(l2tdevtools_update)

    file_content.extend(self._FILE_FOOTER)

    file_content = '\n'.join(file_content)
    file_content = file_content.encode('utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


class DPKGControlWriter(DependencyFileWriter):
  """Dpkg control file writer."""

  _PATH = os.path.join('config', 'dpkg', 'control')

  _FILE_CONTENT = '\n'.join([
      'Source: {project_name:s}',
      'Section: python',
      'Priority: extra',
      'Maintainer: {maintainer:s}',
      ('Build-Depends: debhelper (>= 9), python-all (>= 2.7~), '
       'python-setuptools, python3-all (>= 3.4~), python3-setuptools'),
      'Standards-Version: 3.9.5',
      'X-Python-Version: >= 2.7',
      'X-Python3-Version: >= 3.4',
      'Homepage: {homepage_url:s}',
      '',
      'Package: python-{project_name:s}',
      'Architecture: all',
      ('Depends: {python2_dependencies:s}${{python:Depends}}, '
       '${{misc:Depends}}'),
      'Description: Python 2 module for data type and structure management',
      '{description_long:s}',
      '',
      'Package: python3-{project_name:s}',
      'Architecture: all',
      ('Depends: {python3_dependencies:s}${{python3:Depends}}, '
       '${{misc:Depends}}'),
      'Description: Python 3 module for data type and structure management',
      '{description_long:s}',
      ''])

  def Write(self):
    """Writes a dpkg control file."""
    dependencies = self._dependency_helper.GetDPKGDepends()

    description_long = self._project_definition.description_long
    description_long = '\n'.join([
        ' {0:s}'.format(line) for line in description_long.split('\n')])

    python2_dependencies = ', '.join(dependencies)
    if python2_dependencies:
      python2_dependencies = '{0:s}, '.format(python2_dependencies)

    python3_dependencies = ', '.join(dependencies).replace(
        'python', 'python3')
    if python3_dependencies:
      python3_dependencies = '{0:s}, '.format(python3_dependencies)

    kwargs = {
        'description_long': description_long,
        'description_short': self._project_definition.description_short,
        'homepage_url': self._project_definition.homepage_url,
        'maintainer': self._project_definition.maintainer,
        'project_name': self._project_definition.name,
        'python2_dependencies': python2_dependencies,
        'python3_dependencies': python3_dependencies}
    file_content = self._FILE_CONTENT.format(**kwargs)

    file_content = file_content.encode('utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


class RequirementsWriter(DependencyFileWriter):
  """Requirements.txt file writer."""

  _PATH = 'requirements.txt'

  _FILE_HEADER = ['pip >= 7.0.0']

  def Write(self):
    """Writes a requirements.txt file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = self._dependency_helper.GetInstallRequires()
    for dependency in dependencies:
      file_content.append('{0:s}'.format(dependency))

    file_content = '\n'.join(file_content)
    file_content = file_content.encode('utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


class SetupCfgWriter(DependencyFileWriter):
  """Setup.cfg file writer."""

  _PATH = 'setup.cfg'

  _DOC_FILES = [
      'ACKNOWLEDGEMENTS',
      'AUTHORS',
      'LICENSE',
      'README']

  _FILE_HEADER = '\n'.join([
      '[bdist_rpm]',
      'release = 1',
      'packager = {maintainer:s}',
      'doc_files = {docfiles:s}',
      'build_requires = python-setuptools'])

  def Write(self):
    """Writes a setup.cfg file."""
    docfiles = []
    for path in self._DOC_FILES:
      if os.path.isfile(path):
        docfiles.append(path)

    kwargs = {
        'docfiles': ' '.join(docfiles),
        'maintainer': self._project_definition.maintainer}
    file_header = self._FILE_HEADER.format(**kwargs)

    file_content = [file_header]

    dependencies = self._dependency_helper.GetRPMRequires()
    for index, dependency in enumerate(dependencies):
      if index == 0:
        file_content.append('requires = {0:s}'.format(dependency))
      else:
        file_content.append('           {0:s}'.format(dependency))

    file_content.append('')

    file_content = '\n'.join(file_content)
    file_content = file_content.encode('utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


class TravisBeforeInstallScriptWriter(DependencyFileWriter):
  """Travis-CI install.sh file writer."""

  _PATH = os.path.join('config', 'travis', 'install.sh')

  _FILE_HEADER = [
      '#!/bin/bash',
      '#',
      '# Script to set up Travis-CI test VM.',
      '',
      ('COVERALL_DEPENDENCIES="python-coverage python-coveralls '
       'python-docopt";'),
      '']

  _FILE_FOOTER = [
      '',
      '# Exit on error.',
      'set -e;',
      '',
      'if test ${TRAVIS_OS_NAME} = "osx";',
      'then',
      '\tgit clone https://github.com/log2timeline/l2tdevtools.git;',
      '',
      '\tmv l2tdevtools ../;',
      '\tmkdir dependencies;',
      '',
      ('\tPYTHONPATH=../l2tdevtools ../l2tdevtools/tools/update.py '
       '--download-directory=dependencies ${L2TBINARIES_DEPENDENCIES} '
       '${L2TBINARIES_TEST_DEPENDENCIES};'),
      '',
      'elif test ${TRAVIS_OS_NAME} = "linux";',
      'then',
      '\tsudo add-apt-repository ppa:gift/dev -y;',
      '\tsudo apt-get update -q;',
      '\t# Only install the Python 2 dependencies.',
      ('\t# Also see: https://docs.travis-ci.com/user/languages/python/'
       '#Travis-CI-Uses-Isolated-virtualenvs'),
      ('\tsudo apt-get install -y ${COVERALL_DEPENDENCIES} '
       '${PYTHON2_DEPENDENCIES} ${PYTHON2_TEST_DEPENDENCIES};'),
      'fi',
      '']

  def Write(self):
    """Writes an install.sh file."""
    file_content = []
    file_content.extend(self._FILE_HEADER)

    dependencies = self._dependency_helper.GetL2TBinaries()
    dependencies = ' '.join(dependencies)
    file_content.append('L2TBINARIES_DEPENDENCIES="{0:s}";'.format(
        dependencies))

    file_content.append('')
    file_content.append(
        'L2TBINARIES_TEST_DEPENDENCIES="funcsigs mock pbr six";')

    file_content.append('')

    dependencies = self._dependency_helper.GetDPKGDepends(exclude_version=True)
    dependencies = ' '.join(dependencies)
    file_content.append('PYTHON2_DEPENDENCIES="{0:s}";'.format(dependencies))

    file_content.append('')
    file_content.append('PYTHON2_TEST_DEPENDENCIES="python-mock python-tox";')

    file_content.extend(self._FILE_FOOTER)

    file_content = '\n'.join(file_content)
    file_content = file_content.encode('utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


class ToxIniWriter(DependencyFileWriter):
  """Tox.ini file writer."""

  _PATH = 'tox.ini'

  _FILE_CONTENT = '\n'.join([
      '[tox]',
      'envlist = py2, py3',
      '',
      '[testenv]',
      'pip_pre = True',
      'setenv =',
      '    PYTHONPATH = {{toxinidir}}',
      'deps =',
      '    coverage',
      '    mock',
      '    pytest',
      '    -rrequirements.txt',
      'commands =',
      '    coverage erase',
      ('    coverage run --source={project_name:s} '
       '--omit="*_test*,*__init__*,*test_lib*" run_tests.py'),
      ''])

  def Write(self):
    """Writes a setup.cfg file."""
    kwargs = {'project_name': self._project_definition.name}
    file_content = self._FILE_CONTENT.format(**kwargs)

    file_content = file_content.encode('utf-8')

    with open(self._PATH, 'wb') as file_object:
      file_object.write(file_content)


if __name__ == '__main__':
  project_file = os.path.abspath(__file__)
  project_file = os.path.dirname(project_file)
  project_file = os.path.dirname(project_file)
  project_file = os.path.basename(project_file)
  project_file = '{0:s}.ini'.format(project_file)

  project_reader = utils.projects.ProjectDefinitionReader()
  with open(project_file, 'rb') as file_object:
    project_definition = project_reader.Read(file_object)

  helper = utils.dependencies.DependencyHelper()

  for writer_class in (
      AppveyorYmlWriter, DPKGControlWriter, RequirementsWriter, SetupCfgWriter,
      TravisBeforeInstallScriptWriter, ToxIniWriter):
    writer = writer_class(project_definition, helper)
    writer.Write()
