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
    exports_sources = ["CMakeLists.txt", "patches/*.patch"]
    default_options = {"shared": True, "fPIC": True, "with_snappy": True}
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

        self._cmake = CMake(self)
        if not self.options.with_snappy:
            self._cmake.definitions["SNAPPY_ROOT_DIR"] = ""
        if not self.options.shared:
            self._cmake.definitions["AVRO_DYN_LINK"] = ""
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def requirements(self):
        self.requires("boost/1.75.0")
        if self.options.with_snappy:
            self.requires("snappy/1.1.8")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("avro-release-" + self.version, "source_subfolder")

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
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

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("NOTICE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        # FIXME: avro does not install under a CMake namespace https://github.com/apache/avro/blob/351f589913b9691322966fb77fe72269a0a2ec82/lang/c%2B%2B/CMakeLists.txt#L193
        target = "avrocpp" if self.options.shared else "avrocpp_s"
        self.cpp_info.components[target].libs = [target]
        self.cpp_info.components[target].requires = ["boost::boost"]
        if self.options.with_snappy:
            self.cpp_info.components[target].requires.append("snappy::snappy")
