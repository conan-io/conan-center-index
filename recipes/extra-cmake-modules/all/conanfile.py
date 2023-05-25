import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import get, copy


class ExtracmakemodulesConan(ConanFile):
    name = "extra-cmake-modules"
    license = ("MIT", "BSD-2-Clause", "BSD-3-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://api.kde.org/ecm/"
    topics = ("conan", "cmake", "toolchain", "build-settings")
    description = "KDE's CMake modules"
    no_copy_source = False
    package_type = "build-scripts"
    settings = "build_type"

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_HTML_DOCS"] = False
        tc.cache_variables["BUILD_QTHELP_DOCS"] = False
        tc.cache_variables["BUILD_MAN_DOCS"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()

    def build(self):
        cm_folder = "{}-{}".format(self.name, self.version)
        cmake = CMake(self)
        cmake.configure(build_script_folder=cm_folder)

    def package(self):
        cm_folder = "{}-{}".format(self.name, self.version)
        lic_folder = os.path.join(cm_folder, "LICENSES")
        copy(self, "*", src=lic_folder, dst="licenses")

        cmake = CMake(self)
        cmake.install()

    def package_id(self):
        self.info.settings.clear()

    def package_info(self):
        # this package is CMake files, it doesn't need an extra one generating
        self.cpp_info.set_property("cmake_find_mode", "none")
        self.cpp_info.builddirs.append(os.path.join("share", "ECM", "cmake"))
