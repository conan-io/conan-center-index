import os
import functools
from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.33.0"

class CroncppConan(ConanFile):
    name = "croncpp"
    description = "A C++11/14/17 header-only cross-platform library for handling CRON expressions"
    topics = ("cron", "header-only")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mariusbancila/croncpp/"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake",

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, "11")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def package(self):
        self.copy("LICENSE*", "licenses", self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
