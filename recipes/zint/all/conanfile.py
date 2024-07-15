from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class ZintConan(ConanFile):
    name = "zint"
    description = "Zint Barcode Generator"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/p/zint/code"
    license = "GPL-3.0"
    topics = ("barcode", "qt")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libpng": [True, False],
        "with_qt": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libpng": True,
        "with_qt": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.with_qt:
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_libpng:
            self.requires("libpng/[>=1.6 <2]")
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_qt:
            self.requires("qt/5.15.10")

    def validate(self):
        if self.options.with_qt and not self.dependencies["qt"].options.gui:
            raise ConanInvalidConfiguration(f"{self.ref} needs qt:gui=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DATA_INSTALL_DIR"] = os.path.join(self.package_folder, "lib").replace("\\", "/")
        tc.variables["ZINT_USE_QT"] = self.options.with_qt
        if self.options.with_qt:
            tc.variables["QT_VERSION_MAJOR"] = Version(self.dependencies["qt"].ref.version).major
        tc.variables["ZINT_USE_PNG"] = self.options.with_libpng
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_source(self):
        apply_conandata_patches(self)
        # Don't override CMAKE_OSX_SYSROOT, it can easily break consumers.
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "set(CMAKE_OSX_SYSROOT \"/\")",
            "",
        )

    def build(self):
        self._patch_source()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Zint")

        self.cpp_info.components["libzint"].set_property("cmake_target_name", "Zint::Zint")
        self.cpp_info.components["libzint"].libs = ["zint" if self.options.shared else "zint-static"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["libzint"].defines = ["ZINT_DLL"]
        if self.options.with_libpng:
            self.cpp_info.components["libzint"].requires.extend(["libpng::libpng", "zlib::zlib"])

        if self.options.with_qt:
            self.cpp_info.components["libqzint"].set_property("cmake_target_name", "Zint::QZint")
            self.cpp_info.components["libqzint"].libs = ["QZint"]
            self.cpp_info.components["libqzint"].requires.extend([
                "libzint",
                "qt::qtGui",
            ])
            if self.settings.os == "Windows" and self.options.shared:
                self.cpp_info.components["libqzint"].defines = ["QZINT_DLL"]

        # Trick to only define Zint::QZint and Zint::Zint in CMakeDeps generator
        self.cpp_info.set_property("cmake_target_name", "Zint::QZint" if self.options.with_qt else "Zint::Zint")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Zint"
        self.cpp_info.names["cmake_find_package_multi"] = "Zint"
        self.cpp_info.components["libzint"].names["cmake_find_package"] = "Zint"
        self.cpp_info.components["libzint"].names["cmake_find_package_multi"] = "Zint"
        if self.options.with_qt:
            self.cpp_info.components["libqzint"].names["cmake_find_package"] = "QZint"
            self.cpp_info.components["libqzint"].names["cmake_find_package_multi"] = "QZint"
