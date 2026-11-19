from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.4"


class TypecastConan(ConanFile):
    name = "typecast-c"
    description = "Text-to-Speech API client library for Typecast AI. Pure C with optional C++ wrapper."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/neosapience/typecast-sdk"
    topics = ("tts", "text-to-speech", "speech-synthesis", "typecast", "ai", "voice")
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
    implements = ["auto_shared_fpic"]
    languages = "C"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libcurl/[>=7.78.0 <9]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["TYPECAST_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["TYPECAST_BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["TYPECAST_BUILD_EXAMPLES"] = False
        tc.cache_variables["TYPECAST_BUILD_TESTS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "typecast-c"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=os.path.join(self.source_folder, "typecast-c"),
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "typecast")
        self.cpp_info.set_property("cmake_target_name", "typecast::typecast")

        if self.options.shared:
            self.cpp_info.libs = ["typecast"]
        else:
            self.cpp_info.libs = ["typecast_static"]
            self.cpp_info.defines = ["TYPECAST_STATIC"]


        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["m"]
