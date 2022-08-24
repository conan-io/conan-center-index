import os
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class awskvspicConan(ConanFile):
    name = "aws-kvs-pic"
    license = "Apache-2.0"
    homepage = "https://github.com/awslabs/amazon-kinesis-video-streams-pic"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("Platform Independent Code for Amazon Kinesis Video Streams")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, "fPIC": True}
    generators = "cmake"
    topics = ("aws", "kvs", "kinesis", "video", "stream")
    exports_sources = ["CMakeLists.txt", "patches/*"]
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BUILD_DEPENDENCIES"] = False
            self._cmake.configure()
        return self._cmake

    def validate(self):
        if (self.settings.os != "Linux" and self.options.shared):
            raise ConanInvalidConfiguration("This library can only be built shared on Linux")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.components["kvspic"].libs = ["kvspic"]
        self.cpp_info.components["kvspic"].names["pkg_config"] = "libkvspic"
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["kvspic"].system_libs = ["dl", "rt", "pthread"]

        self.cpp_info.components["kvspicClient"].libs = ["kvspicClient"]
        self.cpp_info.components["kvspicClient"].names["pkg_config"] = "libkvspicClient"

        self.cpp_info.components["kvspicState"].libs = ["kvspicState"]
        self.cpp_info.components["kvspicState"].names["pkg_config"] = "libkvspicState"

        self.cpp_info.components["kvspicUtils"].libs = ["kvspicUtils"]
        self.cpp_info.components["kvspicUtils"].names["pkg_config"] = "libkvspicUtils"
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["kvspicUtils"].system_libs = ["dl", "rt", "pthread"]
