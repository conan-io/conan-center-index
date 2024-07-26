from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.54"

class FreeAlutConan(ConanFile):
    name = "freealut"
    description = "freealut is a free implementation of OpenAL's ALUT standard."
    topics = ("openal", "audio", "api")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://openal.org"
    license = "LGPL-2.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def validate(self):
        # FIXME: freealut supports Windows and Macos, but the recipe needs some help to work.
        if self.settings.os in ["Windows", "Macos"] and \
            not self.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} recipe is currently not prepared for Windows or Macos. Contributions are welcome."
            )

        # freealut's cmake currently is using find_library instead of the package finders so it wouldn't get its public compile definitions.
        # This causes al.h to be preprocessed as a dynamic library. Since Windows symbols are different for dynamic and static methods they aren't found.
        if  self.settings.os == "Windows" and \
            not self.dependencies["openal-soft"].options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} cmake is currently not prepared to use openal-soft as a static library on Windows. Add option openal-soft/*:shared=True."
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("openal-soft/1.22.2", transitive_headers=True, transitive_libs=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeDeps(self)
        tc.generate()
        tc = CMakeToolchain(self)
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0003"] = "NEW"
        tc.variables["BUILD_STATIC"] = not self.options.shared
        # INFO: CMakeDeps generates CamelCase variables
        tc.variables["OPENAL_LIB_DIR"] = os.path.join(self.dependencies["openal-soft"].package_folder, "lib")
        tc.variables["OPENAL_INCLUDE_DIR"] = os.path.join(self.dependencies["openal-soft"].package_folder, "include")
        if self.settings.os == "Windows":            
            tc.variables["OPENAL_INCLUDE_DIR"] += ";" + os.path.join(self.dependencies["openal-soft"].package_folder, "include", "AL")
            tc.variables["OPENAL_LIB_DIR"] = tc.variables["OPENAL_LIB_DIR"].replace("\\","/")
            tc.variables["OPENAL_INCLUDE_DIR"] = tc.variables["OPENAL_INCLUDE_DIR"].replace("\\","/")
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if not self.options.shared:
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ['alut']
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]
        if self.options.shared:
            self.cpp_info.defines.append("ALUT_BUILD_LIBRARY")
