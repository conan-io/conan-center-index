from conan import ConanFile
from conan.tools.files import get, copy, rmdir, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class LibdxfrwConan(ConanFile):
    name = "libdxfrw"
    description = "C++ library to read/write DXF and read DWG files"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/LibreCAD/libdxfrw"
    topics = ("dxf", "dwg", "cad")
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
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["LIBDXFRW_BUILD_DOC"] = False
        tc.generate()

    def build(self):
        if Version(self.version) >= "2.2.0":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "-Werror", "")

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["dxfrw"]

        self.cpp_info.set_property("pkg_config_name", "libdxfrw")

        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH env var: {bin_path}")
        self.env_info.PATH.append(bin_path)
