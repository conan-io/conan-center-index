import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy
from conan.tools.scm import Version

required_conan_version = ">=1.50.0"


class ExtracmakemodulesConan(ConanFile):
    name = "extra-cmake-modules"
    license = ("MIT", "BSD-2-Clause", "BSD-3-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://api.kde.org/ecm/"
    topics = ("cmake", "cmake-modules", "toolchain", "build-settings")
    description = "KDE's CMake modules"
    package_type = "build-scripts"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def build_requirements(self):
        if Version(self.version) >= "5.84.0":
            self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_HTML_DOCS"] = False
        tc.cache_variables["BUILD_QTHELP_DOCS"] = False
        tc.cache_variables["BUILD_MAN_DOCS"] = False
        tc.cache_variables["BUILD_TESTING"] = False

        if self.package_folder is None:
            share_folder = "res"
        else:
            share_folder = os.path.join(self.package_folder, "res").replace("\\", "/")

        tc.cache_variables["SHARE_INSTALL_DIR"] = share_folder
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        lic_folder = os.path.join(self.source_folder, "LICENSES")
        lic_folder_inst = os.path.join(self.package_folder, "licenses")
        copy(self, "*", src=lic_folder, dst=lic_folder_inst)

        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.set_property("cmake_find_mode", "none")

        for dirname in ["cmake", "find-modules", "kde-modules", "toolchain",
                        "modules", "test-modules"]:
            self.cpp_info.builddirs.append(os.path.join("res", "ECM", dirname))
