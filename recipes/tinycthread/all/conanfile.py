from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import msvc_runtime_flag, is_msvc
import functools
import os

required_conan_version = ">=1.33.0"

class TinycthreadConan(ConanFile):
    name = "tinycthread"
    description = "Small, portable implementation of the C11 threads API"
    license = "zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tinycthread/tinycthread"
    topics = ("thread", "c11", "portable")
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["TINYCTHREAD_DISABLE_TESTS"] = True
        cmake.definitions["TINYCTHREAD_INSTALL"] = True
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_license(self):
        file = os.path.join(self.source_folder, self._source_subfolder, "source", "tinycthread.h")
        file_content = tools.files.load(self, file)

        license_start = file_content.find("Copyright")
        license_end = file_content.find("*/")
        license_contents = file_content[license_start:license_end]
        tools.files.save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package(self):
        self._extract_license()
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["tinycthread"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
