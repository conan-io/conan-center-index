import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class LibavrocppConan(ConanFile):
    name = "libavrocpp"
    version = "1.8.2"
    license = "Apache License 2.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Avro is a data serialization system."
    homepage = "https://avro.apache.org/"
    topics = ("serialization", "deserialization")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake", "cmake_find_package"

    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("avro-release-" + self.version, "source_subfolder")
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "project (Avro-cpp)",
            """project (Avro-cpp)
               include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
               conan_basic_setup()""",
        )

    @property
    def _source_subfolder(self):
        return os.path.join("source_subfolder", "lang", "c++")

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("boost/1.75.0")

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("NOTICE", dst="licenses", src=self._source_subfolder)
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["avrocpp"].libs = ["avrocpp"]
        self.cpp_info.components["avrocpp"].requires = ["boost::boost"]

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()
