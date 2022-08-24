import os
import glob
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

class libb2Conan(ConanFile):
    name = "libb2"
    license = ["CC0-1.0", "OpenSSL", "APSL-2.0"]
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/BLAKE2/BLAKE2"
    description = ("libb2 is a library that implemets the BLAKE2 cryptographic hash function, which is faster than MD5, \
                    SHA-1, SHA-2, and SHA-3, yet is at least as secure as the latest standard SHA-3")
    settings = "os", "arch", "compiler", "build_type"
    topics = ("conan", "blake2", "hash")
    exports_sources = ["CMakeLists.txt"]
    generators = ["cmake"]
    options = {"fPIC": [True, False], "shared": [True, False], "use_sse": [True, False], "use_neon": [True, False]}
    default_options = {"fPIC": True, "shared": False, "use_sse": False, "use_neon": False}
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.use_neon and not "arm" in self.settings.arch:
            raise ConanInvalidConfiguration("Neon sources only supported on arm-based CPUs")
        if self.options.use_neon and self.options.use_sse:
            raise ConanInvalidConfiguration("Neon and SSE can not be used together.")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("BLAKE2-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["USE_SSE"] = self.options.use_sse
            self._cmake.definitions["USE_NEON"] = self.options.use_neon
            self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.files.collect_libs(self, self)
        self.cpp_info.includedirs = ["include", os.path.join("include","libb2")]
