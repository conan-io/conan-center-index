import functools
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"

class BZip3Conan(ConanFile):
    name = "bzip3"
    description = "A better and stronger spiritual successor to BZip2."
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kspalaiologos/bzip3"
    topics = ("bzip2", "lzma", "compression")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_thread": [True, False],
        "with_util": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_thread": True,
        "with_util": False,
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_thread

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["WITH_PTHREAD"] = self.options.get_safe("with_thread", False)
        cmake.definitions["WITH_UTIL"] = self.options.with_util
        cmake.definitions["VERSION"] = self.version
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["bzip3"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            if self.options.get_safe("with_thread", False):
                self.cpp_info.system_libs.append("pthread")
