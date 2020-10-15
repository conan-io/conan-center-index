from conans import ConanFile
from conans.errors import ConanException
import os, sys

class CopperSpiceConan(ConanFile):
    name = 'CopperSpice'
    settings = {
        'os': ['Windows'],
        'compiler': {'Visual Studio': {'version': ['16']}},
        'arch': ['x86_64'],
        'build_type': ['Debug', 'Release']
    }
    generators = 'cmake_paths'
    version = '1.7.0'
    license = 'LGPL-2.1-only'
    description = '''
    CopperSpice is a set of individual libraries which can be used to develop cross platform software applications in C++.
    It is a totally open source project released under the LGPL V2.1 license and was initially derived from the Qt framework.
    '''
    url = 'http://balmer.intern.colvistec.de/repos/conan-copperspice'

    def build(self):
        raise ConanException('This recipe cannot be built, it only packages existing binaries. See README.md for details.')

    def package(self):
        src_dir = os.getcwd()
        build_type = str(self.settings.build_type).lower()
        self.copy('**', dst=os.path.join('include'), src=os.path.join(src_dir, build_type, 'include'))
        self.copy('**', dst=os.path.join('bin'), src=os.path.join(src_dir, build_type, 'bin'))
        self.copy('**', dst=os.path.join('lib'), src=os.path.join(src_dir, build_type, 'lib'))
        self.copy('**', dst=os.path.join('CopperSpice', 'cmake'), src=os.path.join(src_dir, build_type, 'cmake', 'CopperSpice'))
