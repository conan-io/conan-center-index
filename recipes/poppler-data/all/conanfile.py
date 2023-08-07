from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import unix_path
import os

required_conan_version = ">=1.52.0"


class PopplerDataConan(ConanFile):
    name = "poppler-data"
    description = "encoding files for use with poppler, enable CJK and Cyrrilic"
    license = ("BSD-3-Clause", "GPL-2.0-or-later", "MIT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://poppler.freedesktop.org/"
    topics = ("poppler", "pdf", "rendering", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _datadir(self):
        return os.path.join(self.package_folder, "res")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["datadir"] = self._datadir.replace("\\", "/")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self._datadir, "pkgconfig"))

    @property
    def _poppler_datadir(self):
        return os.path.join(self._datadir, "poppler")

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "poppler-data")
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]
        self.cpp_info.defines = ["POPPLER_DATADIR={}".format(unix_path(self, self._poppler_datadir))]
        self.conf_info.define("user.poppler-data:datadir", self._poppler_datadir)

        # TODO: to remove in conan v2
        self.user_info.datadir = self._poppler_datadir
