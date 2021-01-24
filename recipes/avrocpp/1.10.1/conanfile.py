import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class LibavrocppConan(ConanFile):
    name = "libavrocpp"
    version = "1.10.1"
    license = "Apache License 2.0"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        compiler = str(self.settings.compiler)
        compiler_version = Version(self.settings.compiler.version.value)

        minimal_version = {
            "Visual Studio": "10",
            "gcc": "4.9.1",
            "clang": "3.3",
            "apple-clang": "5",
        }

        if compiler in minimal_version and compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "%s requires a compiler that supports"
                " at least C++11. %s %s is not"
                " supported." % (self.name, compiler, compiler_version)
            )

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

        if self.options.with_snappy:
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "CMakeLists.txt"),
                "find_package(Snappy)",
                "",
            )

    @property
    def _source_subfolder(self):
        return os.path.join("source_subfolder", "lang", "c++")

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires("boost/[>=1.38.0]")
        if self.options.with_snappy:
            self.requires("snappy/1.1.8")

    def package(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["avrocpp"].libs = ["avrocpp"]
        self.cpp_info.components["avrocpp"].requires = ["boost::boost"]
        if self.options.with_snappy:
            self.cpp_info.components["avrocpp"].requires.append("snappy::snappy")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()
