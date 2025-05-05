from conan import ConanFile
from conan.tools.files import copy, get, apply_conandata_patches, export_conandata_patches, replace_in_file, rmdir
from conans import CMake
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
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"

    _cmake = None
    _qt_version = "5.15.6"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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
                  destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["ADS_VERSION"] = self.version
        self._cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared

        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        apply_conandata_patches(self)

        replace_in_file(self,
            f"{self.source_folder}/{self._source_subfolder}/src/ads_globals.cpp",
            "#include <qpa/qplatformnativeinterface.h>",
            f"#include <{self._qt_version}/QtGui/qpa/qplatformnativeinterface.h>"
        )

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        rmdir(self, os.path.join(self.package_folder, "license"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["qtadvanceddocking"]
        else:
            self.cpp_info.defines.append("ADS_STATIC")
            self.cpp_info.libs = ["qtadvanceddocking_static"]
