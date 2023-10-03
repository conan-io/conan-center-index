from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.32.0"

class LibDispatchConan(ConanFile):
    name = "libdispatch"
    homepage = "https://github.com/apple/swift-corelibs-libdispatch"
    description = "Grand Central Dispatch (GCD or libdispatch) provides comprehensive support for concurrent code execution on multicore hardware."
    topics = ("conan", "libdispatch", "apple", "GCD", "concurrency")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    settings = "os", "compiler", "build_type", "arch"

    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def validate(self):
        if self.settings.compiler != "clang":
            raise ConanInvalidConfiguration("Clang compiler is required.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        copy(self, "LICENSE" , self.source_folder, self.package_folder, keep_path=False)

    def package_info(self):
        if self.settings.os == "Macos":
            self.cpp_info.libs = ["dispatch"]
        else:
            self.cpp_info.libs = ["dispatch", "BlocksRuntime"]

        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["shlwapi", "ws2_32", "winmm", "synchronization"]
