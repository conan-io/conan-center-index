import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=1.52.0"


class HunspellConan(ConanFile):
    name = "hunspell"
    description = "Hunspell is a free spell checker and morphological analyzer library"
    license = ("MPL-1.1", "GPL-2.0-or-later", "LGPL-2.1-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://hunspell.github.io/"
    topics = ("spell", "spell-check")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    no_copy_source = True

    def export_sources(self):
        # FIXME: Remove once the pending upstream PR for CMake support is merged
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # NOTE: The source contains a pre-configured hunvisapi.h and it would
        #       prevent no_copy_source and building without patches.
        h = os.path.join(self.source_folder, "src", "hunspell", "hunvisapi.h")
        os.remove(h)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CONAN_hunspell_VERSION"] = self.version
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.export_sources_folder)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        for license in ["COPYING", "COPYING.LESSER", "license.hunspell"]:
            copy(self, license, dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = ["hunspell"]
        if not self.options.shared:
            self.cpp_info.defines = ["HUNSPELL_STATIC"]
