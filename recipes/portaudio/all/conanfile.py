from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, get, rmdir
import os

class portaudioRecipe(ConanFile):
    name = "portaudio"
    package_type = "library"

    license = "MIT"
    homepage = "https://www.portaudio.com"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A free, cross-platform, open source, audio I/O library."
    topics = ("audio",)

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    implements = ["auto_shared_fpic"]
    languages = "C"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")
    
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        tc.cache_variables["PA_BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["PA_BUILD_SHARED"] = self.options.shared
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        
    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "share"))

    def package_info(self):
        suffix = ""
        if not self.options.shared and self.settings.os == "Windows":
            suffix = "_static"
        target_name = f"portaudio{suffix}"

        if self.settings.arch in ("x86_64", "armv8") and self.settings.os == "Windows":
            suffix += "_x64"
        
        libname = f"portaudio{suffix}"
        self.cpp_info.set_property("cmake_target_name", target_name)
        self.cpp_info.libs = [libname]
        if is_apple_os(self):
            self.cpp_info.frameworks = ["CoreAudio", "AudioToolbox", "AudioUnit", "CoreFoundation", "CoreServices"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["winmm", "dsound", "ole32", "uuid", "setupapi"]
        elif self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "m"]
