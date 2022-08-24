from conan import ConanFile, tools
from conans import CMake
from conan.tools.files import rename
from conan.errors import ConanInvalidConfiguration
import os
import functools

required_conan_version = ">=1.43.0"


class UncrustifyConan(ConanFile):
    name = "uncrustify"
    description = "Code beautifier"
    license = "GPL-2.0-or-later"
    topics = "beautifier", "command-line"
    homepage = "https://github.com/uncrustify/uncrustify"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def validate(self):
        if self.settings.compiler == "gcc" and tools.scm.Version(self, self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration(f"{self.name} requires GCC >=8")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        if self.settings.os == "Windows":
            tools.files.mkdir(self, os.path.join(self.package_folder, "bin"))
            rename(self, os.path.join(self.package_folder, "uncrustify.exe"),
                         os.path.join(self.package_folder, "bin", "uncrustify.exe"))
            os.remove(os.path.join(self.package_folder, "AUTHORS"))
            os.remove(os.path.join(self.package_folder, "BUGS"))
            os.remove(os.path.join(self.package_folder, "COPYING"))
            os.remove(os.path.join(self.package_folder, "ChangeLog"))
            os.remove(os.path.join(self.package_folder, "HELP"))
            os.remove(os.path.join(self.package_folder, "README.md"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "cfg"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "doc"))

        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_id(self):
        del self.info.settings.compiler

    def package_info(self):
        binpath = os.path.join(self.package_folder, "bin")
        self.output.info(f"Adding to PATH: {binpath}")
        self.env_info.PATH.append(binpath)
        self.cpp_info.includedirs = []
