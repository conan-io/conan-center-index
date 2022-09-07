from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools import files
from conan.tools.files import apply_conandata_patches
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.apple import is_apple_os

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
        files.copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            files.copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder='src')

    def requirements(self):
        if not is_apple_os(self):
            self.requires("libiconv/1.17")

    def validate(self):
        if is_msvc_static_runtime(self) and self.options.shared == True:
            raise ConanInvalidConfiguration(f"{self.name} does not support shared and static runtime together.")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        config_h_content = """
#define HAVE_ICONV 1
#define ICONV_CONST
#define PACKAGE_VERSION "{}"
""".format(self.version)
        if self.settings.os == "Macos":
            config_h_content += "#define HAVE_XLOCALE_H 1\n"

        files.save(self, os.path.join(self.source_folder, "include", "config.h"), config_h_content)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["BUILD_CLI"] = self.options.with_cli
        toolchain.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        files.copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["xlsreader"]

        if self.settings.os == "Macos":
            self.cpp_info.system_libs.append("iconv")

        self.cpp_info.set_property("cmake_file_name", "libxls")
        self.cpp_info.set_property("cmake_target_name", "libxls::libxls")

        self.cpp_info.set_property("pkg_config_name", "libxls")

        self.cpp_info.names["cmake_find_package"] = "libxls"
        self.cpp_info.names["cmake_find_package_multi"] = "libxls"

        if not is_apple_os(self):
            self.cpp_info.requires.append("libiconv::libiconv")
