from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps
from conan.tools import files

import os


class QtADS(ConanFile):
    name = "qt-advanced-docking-system"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/githubuser0xFFFF/Qt-Advanced-Docking-System"
    topics = ("qt", "gui")
    description = (source_subfolder
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
    requires = "qt/6.3.1"
    exports_sources = ["patches/**"]
    generators = "CMakeDeps", "CMakeToolchain"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        files.get(self,
                  **self.conan_data["sources"][self.version], 
                  strip_root=True,
                  destination="source_subfolder")
        
    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            files.patch(self, **patch)
        
        qt = self.dependencies["qt"]
        files.replace_in_file(
            self,
            f"{self.source_folder}/source_subfolder/src/ads_globals.cpp",
            "#include <qpa/qplatformnativeinterface.h>",
            f"#include <{qt.ref.version}/QtGui/qpa/qplatformnativeinterface.h>"
        )

    def build(self):
        self._patch_sources()
        
        cmake = CMake(self)
        cmake.configure({
            "ADS_VERSION": self.version,
            "BUILD_EXAMPLES": "OFF",
            "BUILD_STATIC": not self.options.shared,
            }, build_script_folder="source_subfolder")
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        self.copy("LICENSE", dst="licenses", src="source_subfolder")
        files.rmdir(self, os.path.join(self.package_folder, "license"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        if self.options.shared:
            self.cpp_info.libs = ["qtadvanceddocking"]
        else:
            self.cpp_info.defines.append("ADS_STATIC")
            self.cpp_info.libs = ["qtadvanceddocking_static"]
