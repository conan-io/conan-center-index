from conans import ConanFile, CMake, tools
from conans.errors import ConanException
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
import os, sys

class CopperSpiceConan(ConanFile):
    name = 'CopperSpice'
    url = 'https://github.com/conan-io/conan-center-index'
    homepage = 'https://www.copperspice.com/'
    description = '''
    CopperSpice is a set of individual libraries which can be used to develop cross platform software applications in C++.
    It is a totally open source project released under the LGPL V2.1 license and was initially derived from the Qt framework.
    '''
    topics = ("framework", "ui")
    license = 'LGPL-2.1-only'
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
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
        'with_vulkan': [True, False],
        'with_webkit': [True, False],
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
        'with_vulkan': False,
        'with_webkit': False,
        'with_xmlpatterns': False,
    }

    def layout(self):
        cmake_layout(self, src_folder="copperspice")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
#        self.requires("cs_libguarded/[>=1.1.0 <2]")
#        self.requires("libjpeg/9f")
#        self.requires("zlib/1.2.8")
        if self.options.with_mysql_plugin:
            self.options.requires("libmysqlclient/[>=8]")
        if self.options.with_psql_plugin:
            self.options.requires("libpq/[>=9]")
        if self.options.with_sql:
            self.options.requires("sqlite3/[>=3 <4]")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21.1 <4]")
        self.tool_requires("ninja/[>=1.12 <2]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc = CMakeToolchain(self, generator="Ninja")
        tc.variables["WITH_GUI"] = self.options.with_gui
        tc.variables['WITH_MULTIMEDIA'] = self.options.with_multimedia
        tc.variables['WITH_MYSQL_PLUGIN'] = self.options.with_mysql_plugin
        tc.variables['WITH_NETWORK'] = self.options.with_network
        tc.variables['WITH_ODBC_PLUGIN'] = self.options.with_odbc_plugin
        tc.variables['WITH_OPENGL'] = self.options.with_opengl
        tc.variables['WITH_PSQL_PLUGIN'] = self.options.with_psql_plugin
        tc.variables['WITH_SCRIPT'] = self.options.with_script
        tc.variables['WITH_SQL'] = self.options.with_sql
        tc.variables['WITH_SVG'] = self.options.with_svg
        tc.variables['WITH_VULKAN'] = self.options.with_vulkan
        tc.variables['WITH_WEBKIT'] = self.options.with_webkit
        tc.variables['WITH_XMLPATTERNS'] = self.options.with_xmlpatterns
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*", src=os.path.join(self.source_folder, "license"), dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
#        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        # src_dir = os.getcwd()
        # build_type = str(self.settings.arch) + '-' + str(self.settings.build_type).lower()
        # self.copy('**', dst=os.path.join('include'), src=os.path.join(src_dir, build_type, 'include'))
        # self.copy('**', dst=os.path.join('bin'), src=os.path.join(src_dir, build_type, 'bin'))
        # self.copy('**', dst=os.path.join('lib'), src=os.path.join(src_dir, build_type, 'lib'))
        # self.copy('**', dst=os.path.join('CopperSpice', 'cmake'), src=os.path.join(src_dir, build_type, 'cmake', 'CopperSpice'))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CopperSpice")
        self.cpp_info.set_property("pkg_config_name", "copperspice")

        self.cpp_info.names["cmake_find_package"] = "CopperSpice"
