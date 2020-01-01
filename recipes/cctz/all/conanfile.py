import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class CCTZConan(ConanFile):
    name = "cctz"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/cctz"
    description = "C++ library for translating between absolute and civil times"
    topics = ("conan", "cctz", "time", "timezones")
    license = "Apache-2.0"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "build_tools" : [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False, 
        "build_tools": False
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows" and \
           self.settings.compiler == "Visual Studio" and \
           tools.Version(self.settings.compiler.version) < 14:
           raise ConanInvalidConfiguration("CCTZ requires MSVC >= 14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TOOLS"] = self.options.build_tools
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_TESTING"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        # CMake install doesn't package the .dll
        self.copy(pattern="*.dll", dst="bin", keep_path=False)

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if tools.is_apple_os(self.settings.os):
            self.cpp_info.frameworks.append("CoreFoundation")

        if self.options.build_tools:
            bindir = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bindir))
            self.env_info.PATH.append(bindir)
