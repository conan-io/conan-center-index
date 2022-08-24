from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.32.0"

class LibDispatchConan(ConanFile):
    name = "libdispatch"
    homepage = "https://github.com/apple/swift-corelibs-libdispatch"
    description = "Grand Central Dispatch (GCD or libdispatch) provides comprehensive support for concurrent code execution on multicore hardware."
    topics = ("conan", "libdispatch", "apple", "GCD", "concurrency")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"

    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    def validate(self):
        if self.settings.compiler != "clang":
            raise ConanInvalidConfiguration("Clang compiler is required.")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "swift-corelibs-{}-swift-{}-RELEASE".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        if self.settings.os == "Macos":
            self.cpp_info.libs = ["dispatch"]
        else:
            self.cpp_info.libs = ["dispatch", "BlocksRuntime"]

        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["shlwapi", "ws2_32", "winmm", "synchronization"]
