import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class CAFConan(ConanFile):
    name = "caf"
    description = "An open source implementation of the Actor Model in C++"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/actor-framework/actor-framework"
    topics = "conan", "caf", "actor-framework", "actor-model", "pattern-matching", "actors"
    license = "BSD-3-Clause", "BSL-1.0"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "log_level": ["ERROR", "WARNING", "INFO", "DEBUG", "TRACE", "QUIET"],
        "openssl": [True, False]
    }
    default_options = {"shared": False, "fPIC": True, "log_level": "QUIET", "openssl": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    @property
    def _is_static(self):
        return 'shared' not in self.options.values.keys() or not self.options.shared

    @property
    def _has_openssl(self):
        return 'openssl' in self.options.values.keys() and self.options.openssl

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            if self.settings.arch == "x86":
                del self.options.openssl

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("actor-framework-" + self.version, self._source_subfolder)

    def requirements(self):
        if self._has_openssl:
            self.requires("openssl/1.1.1j")

    def configure(self):
        if not self._is_static and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Shared libraries are not supported on Windows")
        compiler_version = Version(self.settings.compiler.version.value)
        if self.version != "0.17.6" and \
            (self.settings.compiler == "gcc" and compiler_version < "7") or \
                (self.settings.compiler == "clang" and compiler_version < "6") or \
                (self.settings.compiler == "apple-clang" and compiler_version < "10") or \
                (self.settings.compiler == "Visual Studio" and compiler_version < "16"):
            raise ConanInvalidConfiguration("caf 0.18.0+ requires a C++17 compiler")
        if self.settings.compiler == "gcc":
            if compiler_version < "4.8":
                raise ConanInvalidConfiguration("g++ >= 4.8 is required, yours is %s" % self.settings.compiler.version)
        elif self.settings.compiler == "clang" and compiler_version < "4.0":
            raise ConanInvalidConfiguration("clang >= 4.0 is required, yours is %s" % self.settings.compiler.version)
        elif self.settings.compiler == "apple-clang" and compiler_version < "9.0":
            raise ConanInvalidConfiguration("clang >= 9.0 is required, yours is %s" % self.settings.compiler.version)
        elif self.settings.compiler == "apple-clang" and compiler_version > "10.0" and \
                self.settings.arch == 'x86':
            raise ConanInvalidConfiguration("clang >= 11.0 does not support x86")
        elif self.settings.compiler == "Visual Studio" and compiler_version < "15":
            raise ConanInvalidConfiguration("Visual Studio >= 15 is required, yours is %s" % self.settings.compiler.version)

    def _cmake_configure(self):
        if not self._cmake:
            self._cmake = CMake(self)
            if self.version == "0.17.6":
                self._cmake.definitions["CMAKE_CXX_STANDARD"] = "11"
                self._cmake.definitions["CAF_NO_AUTO_LIBCPP"] = True
                self._cmake.definitions["CAF_NO_OPENSSL"] = not self._has_openssl
                for define in ["CAF_NO_EXAMPLES", "CAF_NO_TOOLS", "CAF_NO_UNIT_TESTS", "CAF_NO_PYTHON"]:
                    self._cmake.definitions[define] = "ON"
                self._cmake.definitions["CAF_BUILD_STATIC"] = self._is_static
                self._cmake.definitions["CAF_BUILD_STATIC_ONLY"] = self._is_static
            else:
                self._cmake.definitions["CMAKE_CXX_STANDARD"] = "17"
                self._cmake.definitions["CAF_ENABLE_OPENSSL_MODULE"] = self._has_openssl
                for define in ["CAF_ENABLE_EXAMPLES", "CAF_ENABLE_TOOLS", "CAF_ENABLE_TESTING"]:
                    self._cmake.definitions[define] = "OFF"
            if tools.os_info.is_macos and self.settings.arch == "x86":
                self._cmake.definitions["CMAKE_OSX_ARCHITECTURES"] = "i386"
            self._cmake.definitions["CAF_LOG_LEVEL"] = self.options.log_level
            if self.settings.os == 'Windows':
                self._cmake.definitions["OPENSSL_USE_STATIC_LIBS"] = True
                self._cmake.definitions["OPENSSL_MSVC_STATIC_RT"] = True
            elif self.settings.compiler == 'clang':
                self._cmake.definitions["PTHREAD_LIBRARIES"] = "-pthread -ldl"
            else:
                self._cmake.definitions["PTHREAD_LIBRARIES"] = "-pthread"
                if self.settings.compiler == "gcc" and Version(self.settings.compiler.version.value) < "5.0":
                    self._cmake.definitions["CMAKE_SHARED_LINKER_FLAGS"] = "-pthread"
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if "patches" in self.conan_data and self.version in self.conan_data["patches"]:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)
        cmake = self._cmake_configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._cmake_configure()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        suffix = "_static" if self._is_static and self.version == "0.17.6" else ""

        self.cpp_info.names["cmake_find_package"] = "CAF"
        self.cpp_info.names["cmake_find_package_multi"] = "CAF"

        self.cpp_info.components["core"].names["pkg_config"] = f"caf_core{suffix}"
        self.cpp_info.components["core"].libs = [f"caf_core{suffix}"]
        if self.settings.os == "Linux":
            self.cpp_info.components["core"].system_libs = ["pthread", "m"]

        self.cpp_info.components["io"].names["pkg_config"] = f"caf_io{suffix}"
        self.cpp_info.components["io"].libs = [f"caf_io{suffix}"]
        self.cpp_info.components["io"].requires = ["core"]
        if self.settings.os == "Windows":
            self.cpp_info.components["io"].system_libs = ["ws2_32", "iphlpapi", "psapi"]

        if self._has_openssl:
            self.cpp_info.components["openssl"].names["pkg_config"] = f"caf_openssl{suffix}"
            self.cpp_info.components["openssl"].libs = [f"caf_openssl{suffix}"]
            self.cpp_info.components["openssl"].requires = ["io", "openssl::openssl"]
