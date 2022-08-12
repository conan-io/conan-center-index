from conan import ConanFile
from conan import tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout

import os

required_conan_version = ">=1.50.0"

class LibxlsConan(ConanFile):
    name = "libxls"
    description = "a C library which can read Excel (xls) files."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libxls/libxls/"
    topics = ("excel", "xls")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_cli": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_cli": False,
    }

    def export_sources(self):
        tools.files.copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def layout(self):
        cmake_layout(self, src_folder='src')

    def requirements(self):
        self.requires("libiconv/1.17")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        config_h_content =         """
#define HAVE_ICONV 1
#define ICONV_CONST
#define PACKAGE_VERSION "{}"
""".format(self.version)
        if self.settings.os == "Macos":
            config_h_content += "#define HAVE_XLOCALE_H 1\n"

        tools.files.save(self, os.path.join(self.source_folder, "include", "config.h"), config_h_content)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["BUILD_CLI"] = self.options.with_cli
        toolchain.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        tools.files.copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["xlsreader"]

        self.cpp_info.set_property("cmake_file_name", "libxls")
        self.cpp_info.set_property("cmake_target_name", "libxls::libxls")

        self.cpp_info.set_property("pkg_config_name", "libxls")

        self.cpp_info.names["cmake_find_package"] = "libxls"
        self.cpp_info.names["cmake_find_package_multi"] = "libxls"

        self.cpp_info.requires.append("libiconv::libiconv")
