import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class LibavrocppConan(ConanFile):
    name = "libavrocpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Avro is a data serialization system."
    homepage = "https://avro.apache.org/"
    topics = ("serialization", "deserialization")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_snappy": [True, False],
    }
    default_options = {"shared": False, "fPIC": True, "with_snappy": True}
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return os.path.join("source_subfolder", "lang", "c++")

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "project (Avro-cpp)",
            """project (Avro-cpp)
               include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
               conan_basic_setup()""",
        )

        if self.options.with_snappy:
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "CMakeLists.txt"),
                "find_package(Snappy)",
                "",
            )
        self._cmake = CMake(self)
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def requirements(self):
        self.requires("boost/[>=1.38.0]")

    def build_requirements(self):
        self.build_requires("boost/[>=1.38.0]")
        if self.options.with_snappy:
            self.build_requires("snappy/1.1.8")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("avro-release-" + self.version, "source_subfolder")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("NOTICE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        if self.options.shared:
            self.cpp_info.components["avrocpp"].libs = ["avrocpp"]
            self.cpp_info.components["avrocpp"].requires = ["boost::boost"]
        else:
            self.cpp_info.components["avrocpp_s"].libs = ["avrocpp_s"]
            self.cpp_info.components["avrocpp_s"].requires = ["boost::boost"]
