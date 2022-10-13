from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
import os

required_conan_version = ">=1.47.0"


class ZipConan(ConanFile):
    name = "kuba-zip"
    license = "Unlicense"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kuba--/zip"
    description = "A portable, simple zip library written in C"
    topics = ("zip", "compression", "c", "miniz", "portable", "hacking")

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
        tc.variables["CMAKE_DISABLE_TESTING"] = True
        tc.variables["ZIP_STATIC_PIC"] = self.options.get_safe("fPIC", True)
        tc.variables["ZIP_BUILD_DOCS"] = False
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "-Werror", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "UNLICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "zip")
        self.cpp_info.set_property("cmake_target_name", "zip::zip")

        self.cpp_info.names["cmake_find_package"] = "zip"
        self.cpp_info.names["cmake_find_package_multi"] = "zip"

        self.cpp_info.libs = ["zip"]
        if self.options.shared:
            self.cpp_info.defines.append("ZIP_SHARED")
