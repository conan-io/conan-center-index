import functools
import os

from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class HunspellConan(ConanFile):
    name = "hunspell"
    description = (
        "Hunspell is a free spell checker and morphological analyzer library"
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://hunspell.github.io/"
    topics = "spell", "spell-check"
    license = "MPL-1.1", "GPL-2.0-or-later", "LGPL-2.1-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"
    # FIXME: Remove once the pending upstream PR for CMake support is merged
    exports_sources = "CMakeLists.txt"
    no_copy_source = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # NOTE: The source contains a pre-configured hunvisapi.h and it would
        #       prevent no_copy_source and building without patches.
        h = os.path.join(self.source_folder, "src", "hunspell", "hunvisapi.h")
        os.remove(h)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CONAN_hunspell_VERSION"] = self.version
        cmake.configure()
        return cmake

    def build(self):
        self._configure_cmake().build()

    def package(self):
        self._configure_cmake().install()
        self.copy("COPYING", "licenses")
        self.copy("COPYING.LESSER", "licenses")
        self.copy("license.hunspell", "licenses")

    def package_info(self):
        self.cpp_info.libs = ["hunspell"]
        if not self.options.shared:
            self.cpp_info.defines = ["HUNSPELL_STATIC"]
