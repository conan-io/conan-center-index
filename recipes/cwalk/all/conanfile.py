from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class CwalkConan(ConanFile):
    name = "cwalk"
    description = "Path library for C/C++. Cross-Platform for Windows, " \
                  "MacOS and Linux. Supports UNIX and Windows path styles " \
                  "on those platforms."
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "https://likle.github.io/cwalk/"
    topics = ("cwalk", "cross-platform", "windows", "macos", "osx", "linux",
              "path-manipulation", "path", "directory", "file", "file-system",
              "unc", "path-parsing", "file-path")

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["cwalk"]
        if self.options.shared and tools.Version(self.version) >= "1.2.5":
            self.cpp_info.defines.append("CWK_SHARED")
