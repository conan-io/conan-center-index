from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, rmdir, copy
from conan.errors import ConanInvalidConfiguration
import os


class stkRecipe(ConanFile):
    name = "stk"
    package_type = "library"

    # Optional metadata
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://ccrma.stanford.edu/software/stk/"
    description = "The Synthesis ToolKit in C++"
    topics = ("audio", "synthesis")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    implements = ["auto_shared_fpic"]

    # Sources are located in the same place as this recipe, copy them to the recipe
    #exports_sources = "CMakeLists.txt", "src/*", "include/*"
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        if self.settings.compiler == "msvc":
            raise ConanInvalidConfiguration("This library is not supported on MSVC for now, contributions are welcome")

    def requirements(self):
        if self.settings.os == "Linux":
            self.requires("libalsa/1.2.10")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.cache_variables["ENABLE_JACK"] = False
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["BUILD_SHARED"] = self.options.shared
        tc.cache_variables["COMPILE_PROJECTS"] = False  # disable examples
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = ["stk"]

        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["CoreAudio", "CoreFoundation", "CoreMIDI"])
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["winmm", "ole32", "wsock32"]


