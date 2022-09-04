import functools

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class DetoolsConan(ConanFile):
    name = "detools"
    description = "Binary delta encoding"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eerimoq/detools"
    license = "MIT"
    topics = ("delta-compression", "delta-update", "delta-encoding",
              "ota", "bsdiff", "hdiffpatch")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    requires = ['heatshrink/0.4.1', 'lz4/1.9.3', 'xz_utils/5.2.5']

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("This library is only compatible with Linux and FreeBSD")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

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
        self.cpp_info.libs = ["detools"]
