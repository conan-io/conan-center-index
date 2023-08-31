import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class LibgtaConan(ConanFile):
    name = "libgta"
    description = "Library that reads and writes GTA (Generic Tagged Arrays) files."
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://marlam.de/gta"
    topics = ("gta",)

    package_type = "library"
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
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GTA_BUILD_STATIC_LIB"] = not self.options.shared
        tc.variables["GTA_BUILD_SHARED_LIB"] = self.options.shared
        tc.variables["GTA_BUILD_DOCUMENTATION"] = False
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
            "${CMAKE_SOURCE_DIR}",
            "${CMAKE_CURRENT_SOURCE_DIR}")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # https://marlam.de/gta/documentation/ uses GTA as the package name
        self.cpp_info.set_property("cmake_file_name", "GTA")
        self.cpp_info.set_property("cmake_target_name", "GTA::GTA")
        self.cpp_info.set_property("pkg_config_name", "gta")
        self.cpp_info.libs = collect_libs(self)
        if is_msvc(self) and not self.options.shared:
            self.cpp_info.defines.append("GTA_STATIC")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "GTA"
        self.cpp_info.names["cmake_find_package_multi"] = "GTA"
