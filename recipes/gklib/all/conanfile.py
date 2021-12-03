from conans import ConanFile, tools
from conan.tools.cmake import CMakeToolchain, CMake
from conan.tools.files import apply_conandata_patches
from conan.tools.layout import cmake_layout
import os

required_conan_version = ">=1.42.2"


class GKlibConan(ConanFile):
    name = "gklib"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KarypisLab/GKlib"
    description = "A library of various helper routines and frameworks" \
                  " used by many of the lab's software"
    topics = ("karypislab")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    exports_sources = ["patches/**"]

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def layout(self):
        cmake_layout(self)
        self.folders.source = "{}-{}".format(self.name, self.version)

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self.folders.source
        )
        apply_conandata_patches(self)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["BUILD_SHARED_LIBS"] = self.options.shared
        toolchain.variables["ASSERT"] = self.settings.build_type == "Debug"
        toolchain.variables["ASSERT2"] = self.settings.build_type == "Debug"
        toolchain.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        CMake(self).install()
        self.copy("LICENSE.txt", dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "GKlib"
        self.cpp_info.names["cmake_find_package_multi"] = "GKlib"
        self.cpp_info.libs = tools.collect_libs(self)
        if self._is_msvc or self._is_mingw:
            self.cpp_info.defines.append("USE_GKREGEX")
        if self._is_msvc:
            self.cpp_info.defines.append("__thread=__declspec(thread)")
