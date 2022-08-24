import functools
from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration


class PbtoolsConan(ConanFile):
    name = "pbtools"
    description = "A Google Protocol Buffers C library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eerimoq/pbtools"
    license = "MIT"
    topics = ("protobuf", "serialization", "rpc", "protocol-buffers")
    settings = ("os", "compiler", "build_type", "arch")
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("This library is not compatible with Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["pbtools"]
