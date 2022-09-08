from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class OnigurumaConan(ConanFile):
    name = "oniguruma"
    description = "Oniguruma is a modern and flexible regular expressions library."
    license = "BSD-2-Clause"
    topics = ("oniguruma", "regex")
    homepage = "https://github.com/kkos/oniguruma"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "posix_api": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "posix_api": True,
    }

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
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_POSIX_API"] = self.options.posix_api
        tc.variables["ENABLE_BINARY_COMPATIBLE_POSIX_API"] = self.options.posix_api
        if Version(self.version) >= "6.9.8":
            tc.variables["INSTALL_DOCUMENTATION"] = False
            tc.variables["INSTALL_EXAMPLES"] = False
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if Version(self.version) < "6.9.8":
            rmdir(self, os.path.join(self.package_folder, "share"))
        else:
            if self.settings.os == "Windows" and self.options.shared:
                rm(self, "onig-config", os.path.join(self.package_folder, "bin"))
            else:
                rmdir(self, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "oniguruma")
        self.cpp_info.set_property("cmake_target_name", "oniguruma::onig")
        self.cpp_info.set_property("pkg_config_name", "oniguruma")
        # TODO: back to global scope after conan v2 once cmake_find_package_* removed
        self.cpp_info.components["onig"].libs = ["onig"]
        if not self.options.shared:
            self.cpp_info.components["onig"].defines.append("ONIG_STATIC")

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.components["onig"].set_property("cmake_target_name", "oniguruma::onig")
        self.cpp_info.components["onig"].set_property("pkg_config_name", "oniguruma")
        self.cpp_info.components["onig"].names["cmake_find_package"] = "onig"
        self.cpp_info.components["onig"].names["cmake_find_package_multi"] = "onig"
        self.cpp_info.components["onig"].names["pkg_config"] = "oniguruma"
