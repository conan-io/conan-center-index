import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class CoseCStackConan(ConanFile):
    name = "COSE-C"
    license = "BSD-3-Clause"
    homepage = "https://github.com/cose-wg/COSE-C"
    url = "https://github.com/conan-io/conan-center-index"
    description = """Implementation of COSE in C using cn-cbor and openssl"""
    topics = ("cbor")
    exports_sources = ['CMakeLists.txt']
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_mbedtls": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_mbedtls": False
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

    def requirements(self):
        self.requires("cn-cbor/20200227@gocarlos/testing")

        if self.options.use_mbedtls:
            self.requires("mbedtls/2.16.3-gpl")
        else:
            self.requires("openssl/1.1.1d")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + \
            os.path.basename(
                self.conan_data["sources"][self.version]["url"]).split(".")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["coveralls"] = False
        self._cmake.definitions["COSE_C_BUILD_TESTS"] = False
        self._cmake.definitions["COSE_C_BUILD_DOCS"] = False
        self._cmake.definitions["COSE_C_BUILD_DUMPER"] = False
        self._cmake.definitions["COSE_C_USE_MBEDTLS"] = self.options.use_mbedtls
        self._cmake.definitions["COSE_C_USE_PROJECT_ADD"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["cose-c"]
        self.cpp_info.name = "cose-c"
