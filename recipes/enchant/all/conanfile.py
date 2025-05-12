import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get

required_conan_version = ">=1.53.0"


class EnchantConan(ConanFile):
    name = "enchant"
    description = (
        "Enchant aims to provide a simple but comprehensive abstraction for "
        "dealing with different spell checking libraries in a consistent way"
    )
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://rrthomas.github.io/enchant/"
    topics = ("enchant", "spell", "spell-check")

    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        copy(self, "configmake.h", src=self.recipe_folder, dst=self.export_sources_folder)
        copy(self, "configure.cmake", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("glib/2.78.1")
        self.requires("hunspell/1.7.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CONAN_enchant_VERSION"] = self.version
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=self.source_path.parent)
        cmake.build()

    def package(self):
        copy(self, "COPYING.LIB",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["enchant"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl"]
