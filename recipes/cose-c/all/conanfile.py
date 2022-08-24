from from conan import ConanFile, tools
from conans import CMake
import glob
import os


class CoseCConan(ConanFile):
    name = "cose-c"
    license = "BSD-3-Clause"
    homepage = "https://github.com/cose-wg/COSE-C"
    url = "https://github.com/conan-io/conan-center-index"
    description = """Implementation of COSE in C using cn-cbor and openssl"""
    topics = ("cbor")
    exports_sources =  ["CMakeLists.txt", "patches/**"]
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": ["openssl", "mbedtls"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": "openssl"
    }
    generators = "cmake", "cmake_find_package"

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

    def requirements(self):
        self.requires("cn-cbor/1.0.0")

        if self.options.with_ssl == "mbedtls":
            self.requires("mbedtls/2.23.0")
        else:
            self.requires("openssl/1.1.1h")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename(glob.glob("COSE-C-*")[0], self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["COSE_C_COVERALLS"] = False
        self._cmake.definitions["COSE_C_BUILD_TESTS"] = False
        self._cmake.definitions["COSE_C_BUILD_DOCS"] = False
        self._cmake.definitions["COSE_C_BUILD_DUMPER"] = False
        self._cmake.definitions["COSE_C_USE_MBEDTLS"] = self.options.with_ssl == "mbedtls"
        self._cmake.definitions["COSE_C_USE_FIND_PACKAGE"] = True
        self._cmake.definitions["COSE_C_EXPORT_TARGETS"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "secur32", "crypt32", "bcrypt"])
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.extend(["CoreFoundation", "Security"])
        if self.options.with_ssl == "mbedtls":
            self.cpp_info.defines.append("COSE_C_USE_MBEDTLS")
        else:
            self.cpp_info.defines.append("COSE_C_USE_OPENSSL")
