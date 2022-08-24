from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

class CrowConan(ConanFile):
    name = "crow"
    homepage = "https://github.com/ipkn/crow"
    description = "Crow is C++ microframework for web. (inspired by Python Flask)"
    topics = ("conan", "web", "microframework", "header-only")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = ["patches/*"]
    license = "BSD-3-Clause"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("boost/1.69.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        extracted_dir = "crow-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if tools.scm.Version(self.deps_cpp_info["boost"].version) >= "1.70.0":
            raise ConanInvalidConfiguration("Crow requires Boost <1.70.0")

        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy("*.h", dst=os.path.join("include", "crow"), src="amalgamate")

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]
