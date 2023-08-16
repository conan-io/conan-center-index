from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.53.0"

class LibconfigConan(ConanFile):
    name = "libconfig"
    description = "C/C++ library for processing configuration files"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://hyperrealm.github.io/libconfig/"
    topics = ("conf", "config", "cfg", "configuration")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables['BUILD_EXAMPLES'] = False
        tc.variables['BUILD_TESTS'] = False
        if is_apple_os(self):
            tc.preprocessor_definitions["HAVE_XLOCALE_H"] = 1
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        if Version(self.version) == "1.7.2":
            # https://github.com/hyperrealm/libconfig/issues/119
            replace_in_file(self,
                os.path.join(self.source_folder, "lib", "CMakeLists.txt"),
                "_STDLIB_H",
                "")
        if Version(self.version) == "1.7.3":
            replace_in_file(self,
                os.path.join(self.source_folder, "lib", "CMakeLists.txt"),
                "target_compile_definitions(${libname}++ PUBLIC LIBCONFIGXX_STATIC)",
                "target_compile_definitions(${libname}++ PUBLIC LIBCONFIG_STATIC LIBCONFIGXX_STATIC)")

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        prefix = "lib" if Version(self.version) < "1.7.3" or self.settings.os == "Windows" else ""

        self.cpp_info.components["libconfig_"].set_property("cmake_file_name", "libconfig")
        self.cpp_info.components["libconfig_"].set_property("cmake_target_name", "libconfig::libconfig")
        self.cpp_info.components["libconfig_"].set_property("pkg_config_name", "libconfig")
        self.cpp_info.components["libconfig_"].libs = [f"{prefix}config"]

        self.cpp_info.components["libconfig++"].set_property("cmake_file_name", "libconfig")
        self.cpp_info.components["libconfig++"].set_property("cmake_target_name", "libconfig::libconfig++")
        self.cpp_info.components["libconfig++"].set_property("pkg_config_name", "libconfig++")
        self.cpp_info.components["libconfig++"].libs = [f"{prefix}config++"]
        self.cpp_info.components["libconfig++"].requires = ["libconfig_"]

        if not self.options.shared:
            self.cpp_info.components["libconfig_"].defines.append("LIBCONFIG_STATIC")
            self.cpp_info.components["libconfig++"].defines.append("LIBCONFIGXX_STATIC")
        if self.settings.os == "Windows":
            self.cpp_info.components["libconfig_"].system_libs.append("shlwapi")
            self.cpp_info.components["libconfig++"].system_libs.append("shlwapi")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libconfig_"].names["cmake_find_package"] = "libconfig"
        self.cpp_info.components["libconfig_"].names["cmake_find_package_multi"] = "libconfig"
        self.cpp_info.components["libconfig_"].names["pkg_config"] = "libconfig"

        self.cpp_info.components["libconfig++"].names["cmake_find_package"] = "libconfig++"
        self.cpp_info.components["libconfig++"].names["cmake_find_package_multi"] = "libconfig++"
        self.cpp_info.components["libconfig++"].names["pkg_config"] = "libconfig++"
