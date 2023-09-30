from conan import ConanFile
from conan.tools.files import copy, get, apply_conandata_patches, export_conandata_patches, replace_in_file, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.52.0"

class QtADS(ConanFile):
    name = "qt-advanced-docking-system"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/githubuser0xFFFF/Qt-Advanced-Docking-System"
    topics = ("qt", "gui")
    description = (
        "Qt Advanced Docking System lets you create customizable layouts "
        "using a full featured window docking system similar to what is found "
        "in many popular integrated development environments (IDEs) such as "
        "Visual Studio."
    )
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "CMakeDeps"

    _qt_version = "5.15.10"

    def layout(self):
        cmake_layout(self)

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires(f"qt/{self._qt_version}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self.source_folder)

    def _patch_sources(self):
        apply_conandata_patches(self)

        replace_in_file(self,
            f"{self.source_folder}/src/ads_globals.cpp",
            "#include <qpa/qplatformnativeinterface.h>",
            f"#include <{self._qt_version}/QtGui/qpa/qplatformnativeinterface.h>"
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ADS_VERSION"] = self.version
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_STATIC"] = not self.options.shared
        tc.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", dst="licenses", src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "license"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["qtadvanceddocking"]
        else:
            self.cpp_info.defines.append("ADS_STATIC")
            self.cpp_info.libs = ["qtadvanceddocking_static"]
