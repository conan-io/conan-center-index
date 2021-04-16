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
        "log_level": ["error", "warning", "info", "debug", "trace", "quiet"],
        "with_openssl": [True, False]
    }
    default_options = {"shared": False, "fPIC": True, "log_level": "quiet", "with_openssl": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("actor-framework-" + self.version, self._source_subfolder)

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1j")

    def _minimum_compilers_version(self, cppstd):
        standards = {
            "11": {
                "Visual Studio": "15",
                "gcc": "4.8",
                "clang": "4",
                "apple-clang": "9",
            },
            "17": {
                "Visual Studio": "16",
                "gcc": "7",
                "clang": "6",   # Should be 5 but clang 5 has a bug that breaks compiling CAF
                                # see https://github.com/actor-framework/actor-framework/issues/1226
                "apple-clang": "10",
            },
        }
        return standards.get(cppstd) or {}

    @property
    def _cppstd(self):
        return "11" if Version(self.version) <= "0.17.6" else "17"

    def validate(self):
        min_version = self._minimum_compilers_version(self._cppstd).get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._cppstd, self.settings.compiler, self.settings.compiler.version))

        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) > "10.0" and \
                self.settings.arch == 'x86':
            raise ConanInvalidConfiguration("clang >= 11.0 does not support x86")
        if self.options.shared and self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Shared libraries are not supported on Windows")
        if self.options.with_openssl and self.settings.os == "Windows" and self.settings.arch == "x86":
            raise ConanInvalidConfiguration("OpenSSL is not supported for Windows x86")

    def _cmake_configure(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["CMAKE_CXX_STANDARD"] = self._cppstd
            if Version(self.version) <= "0.17.6":
                self._cmake.definitions["CAF_NO_AUTO_LIBCPP"] = True
                self._cmake.definitions["CAF_NO_OPENSSL"] = not self.options.with_openssl
                for define in ["CAF_NO_EXAMPLES", "CAF_NO_TOOLS", "CAF_NO_UNIT_TESTS", "CAF_NO_PYTHON"]:
                    self._cmake.definitions[define] = "ON"
                self._cmake.definitions["CAF_BUILD_STATIC"] = not self.options.shared
                self._cmake.definitions["CAF_BUILD_STATIC_ONLY"] = not self.options.shared
            else:
                self._cmake.definitions["CAF_ENABLE_OPENSSL_MODULE"] = self.options.with_openssl
                for define in ["CAF_ENABLE_EXAMPLES", "CAF_ENABLE_TOOLS", "CAF_ENABLE_TESTING"]:
                    self._cmake.definitions[define] = "OFF"
            self._cmake.definitions["CAF_LOG_LEVEL"] = self.options.log_level.value.upper()
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._cmake_configure()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)
        cmake = self._cmake_configure()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        suffix = "_static" if not self.options.shared and Version(self.version) <= "0.17.6" else ""

        self.cpp_info.names["cmake_find_package"] = "CAF"
        self.cpp_info.names["cmake_find_package_multi"] = "CAF"

        self.cpp_info.components["caf_core"].names["cmake_find_package"] = "core"
        self.cpp_info.components["caf_core"].names["cmake_find_package_multi"] = "core"
        self.cpp_info.components["caf_core"].libs = ["caf_core{}".format(suffix)]
        if self.settings.os == "Windows":
            self.cpp_info.components["caf_core"].system_libs = ["iphlpapi"]
        elif self.settings.os == "Linux":
            self.cpp_info.components["caf_core"].system_libs = ["pthread", "m"]

        self.cpp_info.components["caf_io"].names["cmake_find_package"] = "io"
        self.cpp_info.components["caf_io"].names["cmake_find_package_multi"] = "io"
        self.cpp_info.components["caf_io"].libs = ["caf_io{}".format(suffix)]
        self.cpp_info.components["caf_io"].requires = ["caf_core"]
        if self.settings.os == "Windows":
            self.cpp_info.components["caf_io"].system_libs = ["ws2_32"]

        if self.options.with_openssl:
            self.cpp_info.components["caf_openssl"].names["cmake_find_package"] = "openssl"
            self.cpp_info.components["caf_openssl"].names["cmake_find_package_multi"] = "openssl"
            self.cpp_info.components["caf_openssl"].libs = ["caf_openssl{}".format(suffix)]
            self.cpp_info.components["caf_openssl"].requires = ["caf_io", "openssl::openssl"]
