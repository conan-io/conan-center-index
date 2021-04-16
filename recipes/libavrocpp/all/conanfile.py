import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class LibavrocppConan(ConanFile):
    name = "libavrocpp"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Avro is a data serialization system."
    homepage = "https://avro.apache.org/"
    topics = ("serialization", "deserialization")
    exports_sources = ["CMakeLists.txt", "patches/*.patch"]
    generators = "cmake", "cmake_find_package"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return os.path.join("source_subfolder", "lang", "c++")

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def requirements(self):
        self.requires("boost/1.75.0")
        self.requires("snappy/1.1.8")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("avro-release-" + self.version, "source_subfolder")

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "${SNAPPY_LIBRARIES}", "${Snappy_LIBRARIES}"
        )

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["SNAPPY_ROOT_DIR"] = self.deps_cpp_info["snappy"].rootpath.replace("\\", "/")
            self._cmake.configure()
        return self._cmake

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
        self.cpp_info.components[target].requires = ["boost::boost", "snappy::snappy"]
        if self.options.shared:
            self.cpp_info.components[target].defines.append("AVRO_DYN_LINK")
