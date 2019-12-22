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

    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TOOLS"] = self.options.build_tools
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_TESTING"] = False
        cmake.configure()
        cmake.build()

    def package(self):
        include_folder = os.path.join(self._source_subfolder, "include")
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if tools.is_apple_os(self.settings.os):
            self.cpp_info.frameworks.append("CoreFoundation")
