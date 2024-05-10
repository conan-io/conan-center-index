from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rm, rmdir
import os

required_conan_version = ">=1.53.0"


class BmxConan(ConanFile):
    name = "bmx"
    description = (
        "Library for handling broadcast/production oriented media file formats. "
        "Allows reading, modifying and writing media metadata and file essences."
    )
    topics = ("vfx", "image", "picture", "video", "multimedia", "mxf")
    license = "BSD-3-Clause"
    homepage = "https://github.com/bbc/bmx"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libcurl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libcurl": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        # Required libraries
        self.requires("uriparser/0.9.8")
        self.requires("expat/2.6.2")

        if not (self.settings.os == 'Windows' or self.settings.os == 'Macos'):
            self.requires('libuuid/1.0.3')

        # Configuration dependent requirements
        if self.options.with_libcurl:
            self.requires("libcurl/8.6.0")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    @staticmethod
    def _conan_comp(name):
        return f"bmx_{name.lower()}"

    def _add_component(self, name):
        component = self.cpp_info.components[self._conan_comp(name)]
        component.set_property("cmake_target_name", f"bmx::{name}")
        component.names["cmake_find_package"] = name
        component.names["cmake_find_package_multi"] = name
        return component

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "bmx")
        self.cpp_info.set_property("pkg_config_name", "bmx")

        self.cpp_info.names["cmake_find_package"] = "bmx"
        self.cpp_info.names["cmake_find_package_multi"] = "bmx"

        # bbc-bmx::MXF
        libmxf = self._add_component("MXF")
        libmxf.libs = ["MXF"]
        libmxf.requires = []
        if not (self.settings.os == 'Windows' or self.settings.os == 'Macos'):
            libmxf.requires.append("libuuid::libuuid")

        # bbc-bmx::MXF++
        libmxfpp = self._add_component("MXF++")
        libmxfpp.libs = ["MXF++"]
        libmxfpp.requires = [
            "bmx_mxf"
        ]

        # bbc-bmx::bmx
        libbmx = self._add_component("bmx")
        libbmx.libs = ["bmx"]
        libbmx.requires = [
            "bmx_mxf",
            "bmx_mxf++",
            "expat::expat",
            "uriparser::uriparser",
        ]
        if not (self.settings.os == 'Windows' or self.settings.os == 'Macos'):
            libbmx.requires.append("libuuid::libuuid")

        if self.options.with_libcurl:
            libbmx.requires.append("libcurl::libcurl")
