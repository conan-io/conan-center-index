import os
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class CCTZConan(ConanFile):
    name = "cctz"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/cctz"
    description = "C++ library for translating between absolute and civil times"
    topics = ("conan", "cctz", "time", "timezones")
    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "build_tools" : [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "build_tools": True
    }

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

    def validate(self):
        if self.settings.compiler == "Visual Studio" and \
           tools.scm.Version(self, self.settings.compiler.version) < 14:
            raise ConanInvalidConfiguration("CCTZ requires MSVC >= 14")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TOOLS"] = self.options.build_tools
        self._cmake.definitions["BUILD_EXAMPLES"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "cctz"
        self.cpp_info.names["cmake_find_package_multi"] = "cctz"
        self.cpp_info.libs = ["cctz"]
        if tools.is_apple_os(self, self.settings.os):
            self.cpp_info.frameworks.append("CoreFoundation")

        if self.options.build_tools:
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bindir))
            self.env_info.PATH.append(bindir)
