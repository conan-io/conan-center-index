from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.build import check_min_cppstd
import os

required_conan_version = ">=1.53.0"


class ZintConan(ConanFile):
    name = "zint"
    description = "Zint Barcode Generator - an encoding library supporting over 50 symbologies"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.zint.org.uk"
    license = "BSD-3-Clause"
    topics = ("barcode", "qrcode", "datamatrix", "pdf417", "aztec")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libpng": [True, False],
        "with_qt": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "with_libpng": True,
        "with_qt": False,
    }

    def export_sources(self):
        copy(self, "*", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_qt:
            # Pure C library
            self.settings.rm_safe("compiler.libcxx")
            self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_libpng:
            self.requires("libpng/[>=1.6 <2]")
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_qt:
            self.requires("qt/[>=5.15 <7]")

    def validate(self):
        if self.options.with_qt:
            check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ZINT_SHARED"] = self.options.shared
        tc.variables["ZINT_STATIC"] = not self.options.shared
        tc.variables["ZINT_USE_PNG"] = self.options.with_libpng
        tc.variables["ZINT_USE_QT"] = self.options.with_qt
        tc.variables["ZINT_USE_GS1SE"] = False
        tc.variables["ZINT_UNINSTALL"] = False
        tc.variables["ZINT_TEST"] = False
        tc.variables["ZINT_FRONTEND"] = False
        tc.variables["ZINT_USE_QT"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))


    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "zint")

        self.cpp_info.components["libzint"].set_property("cmake_target_name", "zint::zint")
        self.cpp_info.components["libzint"].libs = ["zint" if self.options.shared else "zint-static"]
        self.cpp_info.components["libzint"].includedirs = ["include"]
        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.components["libzint"].defines = ["ZINT_DLL"]
        if self.options.with_libpng:
            self.cpp_info.components["libzint"].requires = ["libpng::libpng", "zlib::zlib"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["libzint"].system_libs = ["m"]

        if self.options.with_qt:
            self.cpp_info.components["qzint"].set_property("cmake_target_name", "zint::QZint")
            self.cpp_info.components["qzint"].libs = ["QZint"]
            self.cpp_info.components["qzint"].includedirs = ["include"]
            self.cpp_info.components["qzint"].requires = ["libzint", "qt::qt"]

## testing manually notes
## conan create all --version="2.16.0" -pr:h default -pr:b default -o "zint/*:shared=True"
# conan create . -s compiler.cppstd=17