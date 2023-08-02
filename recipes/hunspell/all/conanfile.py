from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

class HunspellConan(ConanFile):
    name = "hunspell"
    description = (
        "Hunspell is a free spell checker and morphological analyzer library"
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://hunspell.github.io/"
    topics = "spell", "spell-check"
    license = "MPL-1.1", "GPL-2.0-or-later", "LGPL-2.1-or-later"

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

    @property
    def _minimum_cpp_standard(self):
        return 11

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "7",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if min_version:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(f"{self.name} requires at least {self.settings.compiler} {min_version}")

    def export_sources(self):
        # TODO: Remove once PR is merged: https://github.com/hunspell/hunspell/pull/704/
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
        tc.variables["HUNSPELL_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["CONAN_hunspell_VERSION"] = self.version
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "COPYING*",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"),
             keep_path=False)
        copy(self, "license.hunspell",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"),
             keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["hunspell"]
        if not self.options.shared:
            self.cpp_info.defines = ["HUNSPELL_STATIC"]
