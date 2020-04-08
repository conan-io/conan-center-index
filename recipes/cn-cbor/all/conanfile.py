import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class CnCborStackConan(ConanFile):
    name = "cn-cbor"
    license = "MIT"
    homepage = "https://github.com/jimsch/cn-cbor/"
    url = "https://github.com/conan-io/conan-center-index"
    description = """A constrained node implementation of CBOR in C"""
    topics = ("cbor")
    exports_sources = ['CMakeLists.txt']
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + os.path.basename(self.conan_data["sources"][self.version]["url"]).split(".")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["fatal_warnings"] = False
        self._cmake.definitions["coveralls"] = False
        self._cmake.definitions["build_tests"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst='licenses', src=os.path.join(self._source_subfolder, "license"))
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
