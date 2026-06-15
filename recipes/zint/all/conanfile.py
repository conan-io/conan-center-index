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
    homepage = "https://www.zint.org.uk"
    license = "BSD-3-Clause", "GPL-3.0"
    topics = ("barcode", "barcode-generator", "qr-code", "2d-barcodes", "gs1")

    def init(self):
        if Version(self.version) < "2.16.0":
            self.license = "GPL-3.0"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libpng": [True, False],
        "with_qt": [True, False],
        "with_gs1se": [True, False],
        "with_qt6": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libpng": True,
        "with_qt": False,
        "with_gs1se": False,
        "with_qt6": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "2.16.0":
            del self.options.with_gs1se
            del self.options.with_qt6

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
            if self.options.get_safe("with_qt6"):
                self.requires("qt/[>=6.0 <7]")
            else:
                self.requires("qt/5.15.10")

    def validate(self):
        if self.options.with_qt and not self.dependencies["qt"].options.gui:
            raise ConanInvalidConfiguration(f"{self.ref} needs qt:gui=True")
        if self.options.get_safe("with_qt6") and not self.options.with_qt:
            raise ConanInvalidConfiguration(f"{self.ref}: with_qt6=True requires with_qt=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DATA_INSTALL_DIR"] = os.path.join(self.package_folder, "lib").replace("\\", "/")
        tc.variables["ZINT_USE_QT"] = self.options.with_qt
        if self.options.with_qt:
            tc.variables["QT_VERSION_MAJOR"] = Version(self.dependencies["qt"].ref.version).major
        tc.variables["ZINT_USE_PNG"] = self.options.with_libpng
        if Version(self.version) >= "2.16.0":
            # 2.16.0+ uses explicit ZINT_SHARED/ZINT_STATIC instead of BUILD_SHARED_LIBS
            tc.variables["ZINT_SHARED"] = self.options.shared
            tc.variables["ZINT_STATIC"] = not self.options.shared
            tc.variables["ZINT_FRONTEND"] = False
            tc.variables["ZINT_USE_GS1SE"] = self.options.with_gs1se
            tc.variables["ZINT_QT6"] = self.options.with_qt6
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_source(self):
        apply_conandata_patches(self)
        if Version(self.version) < "2.16.0":
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
        # 2.16.0 upstream uses OUTPUT_NAME "zint" on non-Windows for static builds;
        # 2.10.0's patch forced "zint-static" on all platforms.
        use_static_suffix = not self.options.shared and (
            Version(self.version) < "2.16.0" or self.settings.os == "Windows"
        )
        self.cpp_info.components["libzint"].libs = ["zint-static" if use_static_suffix else "zint"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["libzint"].defines = ["ZINT_DLL"]
        if self.settings.os != "Windows":
            self.cpp_info.components["libzint"].system_libs = ["m"]
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

        if Version(self.version) < "2.16.0":
            # Conan 1 cmake_find_package* generator support — not needed for 2.16.0+
            self.cpp_info.names["cmake_find_package"] = "Zint"
            self.cpp_info.names["cmake_find_package_multi"] = "Zint"
            self.cpp_info.components["libzint"].names["cmake_find_package"] = "Zint"
            self.cpp_info.components["libzint"].names["cmake_find_package_multi"] = "Zint"
            if self.options.with_qt:
                self.cpp_info.components["libqzint"].names["cmake_find_package"] = "QZint"
                self.cpp_info.components["libqzint"].names["cmake_find_package_multi"] = "QZint"
