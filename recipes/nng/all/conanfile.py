#DISCLAIMER: This recipe is heavily based on the recipe created by GavinNL under https://github.com/uilianries/conan-nng

from conans import ConanFile, CMake, tools
import os


class NngConan(ConanFile):
    name = "nng"
    version = "1.3.0"
    url="https://github.com/nanomsg/nng"
    description = "A networking library that provides several common communication patterns"
    license = "MIT"
    exports = ["LICENSE.txt"]
    settings = "os", "compiler", "arch", "build_type"
    short_paths = True
    generators = "cmake"
    options = {
        "shared": [True, False],
        "enable_tests": [True, False],
        "enable_tools": [True, False],
        "enable_nngcat": [True, False],
	    "fPIC" : [True, False]
    }
    default_options = (
        "shared=False",
        "enable_tests=False",
        "enable_tools=False",
        "enable_nngcat=False",
	    "fPIC=True"
    )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        url = self.conan_data["sources"][self.version]["url"]
        extracted_dir = "nng-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["NNG_TESTS"] = self.options.enable_tests
        cmake.definitions["NNG_ENABLE_TOOLS"] = self.options.enable_tools
        cmake.definitions["NNG_ENABLE_NNGCAT"] = self.options.enable_nngcat
        cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.configure(source_folder = self._source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy("*.h", dst="include", src="install/include")
        self.copy("*.dll", dst="bin", src="install/bin")
        self.copy("*.lib", dst="lib", src="install/lib")
        self.copy("*.a", dst="lib", src="install/lib")
        self.copy("*.so*", dst="lib", src="install/lib")
        self.copy("*.dylib", dst="lib", src="install/lib")
        self.copy("nngcat*", dst="bin", src="install/bin")
        self.copy("*.*", dst="lib/pkgconfig", src="install/lib/pkgconfig")

    def package_info(self):
        self.cpp_info.libs = ["nng"]

        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.libs.append('mswsock')
                self.cpp_info.libs.append('ws2_32')
        elif self.settings.os == "Linux":
            self.cpp_info.libs.append('pthread')
            pass

