import functools

from conan import ConanFile, tools
from conans import CMake

required_conan_version = ">=1.43.0"


class EnchantConan(ConanFile):
    name = "enchant"
    description = (
        "Enchant aims to provide a simple but comprehensive abstraction for "
        "dealing with different spell checking libraries in a consistent way"
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://abiword.github.io/enchant/"
    topics = "enchant", "spell", "spell-check"
    license = "LGPL-2.1-or-later"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package_multi"
    requires = "glib/2.71.3", "hunspell/1.7.0"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        self.copy("configmake.h")
        self.copy("configure.cmake")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def source(self):
        root = self._source_subfolder
        get_args = self.conan_data["sources"][self.version]
        tools.files.get(self, **get_args, destination=root, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CONAN_enchant_VERSION"] = self.version
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        self._configure_cmake().build()

    def package(self):
        self.copy("COPYING.LIB", "licenses", self._source_subfolder)
        self._configure_cmake().install()

    def package_info(self):
        self.cpp_info.libs = ["enchant"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl"]
