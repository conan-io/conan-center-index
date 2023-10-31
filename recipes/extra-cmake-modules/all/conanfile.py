import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import get, copy
from conan.tools.scm import Version


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
    short_paths = True

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder
        )

    def build_requirements(self):
        if self.version <= Version("5.80.0"):
            self.tool_requires("cmake/[>=3.5]")
        else:
            self.tool_requires("cmake/[>=3.16]")


    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_HTML_DOCS"] = False
        tc.cache_variables["BUILD_QTHELP_DOCS"] = False
        tc.cache_variables["BUILD_MAN_DOCS"] = False
        tc.cache_variables["BUILD_TESTING"] = False

        if self.package_folder is None:
            share_folder = "res"
        else:
            share_folder = os.path.join(self.package_folder, "res")

        tc.cache_variables["SHARE_INSTALL_DIR"] = share_folder
        tc.generate()

    def build(self):
        cm_folder = "{}-{}".format(self.name, self.version)
        cmake = CMake(self)
        cmake.configure(build_script_folder=cm_folder)

    def package(self):
        cm_folder = "{}-{}".format(self.name, self.version)
        lic_folder_st = os.path.join(cm_folder, "LICENSES")
        lic_folder = os.path.join(self.source_folder, lic_folder_st)

        lic_folder_inst = os.path.join(self.package_folder, "licenses")
        copy(self, "*", src=lic_folder, dst=lic_folder_inst)

        cmake = CMake(self)
        cmake.install()

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.set_property("cmake_find_mode", "none")

        for dirname in ["cmake", "find-modules", "kde-modules", "toolchain",
                        "modules", "test-modules"]:
            self.cpp_info.builddirs.append(os.path.join("res", "ECM", dirname))
