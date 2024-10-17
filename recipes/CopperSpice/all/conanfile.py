from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import os, sys

class CopperSpiceConan(ConanFile):
    name = 'CopperSpice'
    settings = {
        'os': ['Windows'],
        'compiler': {'Visual Studio': {'version': ['16']}},
        'arch': ['x86_64', 'x86'],
        'build_type': ['Debug', 'Release']
    }
    generators = 'cmake_paths'
    version = '1.7.1'
    license = 'LGPL-2.1-only'
    description = '''
    CopperSpice is a set of individual libraries which can be used to develop cross platform software applications in C++.
    It is a totally open source project released under the LGPL V2.1 license and was initially derived from the Qt framework.
    '''
    url = 'http://balmer.intern.colvistec.de/repos/_51' # conan-copperspice repo
    homepage = 'https://www.copperspice.com/'
    exports_sources = ['patches/*']
    options = {
        'with_gui': [True, False],
        'with_multimedia': [True, False],
        'with_mysql_plugin': [True, False],
        'with_network': [True, False],
        'with_odbc_plugin': [True, False],
        'with_opengl': [True, False],
        'with_psql_plugin': [True, False],
        'with_script': [True, False],
        'with_sql': [True, False],
        'with_svg': [True, False],
        'with_webkit': [True, False],
        'with_xml': [True, False],
        'with_xmlpatterns': [True, False],
    }

    default_options = {
        'with_gui': True,
        'with_multimedia': False,
        'with_mysql_plugin': False,
        'with_network': False,
        'with_odbc_plugin': False,
        'with_opengl': False,
        'with_psql_plugin': False,
        'with_script': False,
        'with_sql': False,
        'with_svg': False,
        'with_webkit': False,
        'with_xml': True,
        'with_xmlpatterns': False,
    }

    def source(self):
        git = tools.Git(folder='copperspice')
        tag = 'cs-{}'.format(self.version)
        git.clone('https://github.com/copperspice/copperspice', branch=tag, shallow=True)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['WITH_GUI'] = self.options.with_gui
        cmake.definitions['WITH_MULTIMEDIA'] = self.options.with_multimedia
        cmake.definitions['WITH_MYSQL_PLUGIN'] = self.options.with_mysql_plugin
        cmake.definitions['WITH_NETWORK'] = self.options.with_network
        cmake.definitions['WITH_ODBC_PLUGIN'] = self.options.with_odbc_plugin
        cmake.definitions['WITH_OPENGL'] = self.options.with_opengl
        cmake.definitions['WITH_PSQL_PLUGIN'] = self.options.with_psql_plugin
        cmake.definitions['WITH_SCRIPT'] = self.options.with_script
        cmake.definitions['WITH_SQL'] = self.options.with_sql
        cmake.definitions['WITH_SVG'] = self.options.with_svg
        cmake.definitions['WITH_WEBKIT'] = self.options.with_webkit
        cmake.definitions['WITH_XML'] = self.options.with_xml
        cmake.definitions['WITH_XMLPATTERNS'] = self.options.with_xmlpatterns
        cmake.configure(source_dir='copperspice')
        return cmake

    def build(self):
        tools.patch(base_path='copperspice', patch_file='patches/noifc.patch')
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        # src_dir = os.getcwd()
        # build_type = str(self.settings.arch) + '-' + str(self.settings.build_type).lower()
        # self.copy('**', dst=os.path.join('include'), src=os.path.join(src_dir, build_type, 'include'))
        # self.copy('**', dst=os.path.join('bin'), src=os.path.join(src_dir, build_type, 'bin'))
        # self.copy('**', dst=os.path.join('lib'), src=os.path.join(src_dir, build_type, 'lib'))
        # self.copy('**', dst=os.path.join('CopperSpice', 'cmake'), src=os.path.join(src_dir, build_type, 'cmake', 'CopperSpice'))
