from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class ZintConan(ConanFile):
    name = "zint"
    description = "Zint Barcode Generator"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.zint.org.uk"
    license = ("BSD-3-Clause", "GPL-3.0")
    topics = ("barcode", "barcode-generator", "qr-code", "2d-barcodes", "gs1")
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
            self.requires("qt/[>=5.15 <7]", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if self.options.with_qt and not self.dependencies["qt"].options.gui:
            raise ConanInvalidConfiguration(f"{self.ref} needs qt:gui=True")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ZINT_USE_QT"] = self.options.with_qt
        if self.options.with_qt:
            qt_version = Version(self.dependencies["qt"].ref.version)
            tc.variables["QT_VERSION_MAJOR"] = str(qt_version.major)
            tc.variables["ZINT_QT6"] = qt_version.major == "6"
        tc.cache_variables["ZINT_USE_PNG"] = self.options.with_libpng
        tc.cache_variables["ZINT_SHARED"] = self.options.shared
        tc.cache_variables["ZINT_STATIC"] = not self.options.shared
        # disabling front-end compilation is intentional
        tc.cache_variables["ZINT_FRONTEND"] = False
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Zint")
        self.cpp_info.components["libzint"].set_property("cmake_target_name", "Zint::Zint")
        use_static_suffix = not self.options.shared and self.settings.os == "Windows"
        self.cpp_info.components["libzint"].libs = ["zint-static" if use_static_suffix else "zint"]
        if self.settings.os != "Windows":
            self.cpp_info.components["libzint"].system_libs = ["m"]
        if self.options.with_libpng:
            self.cpp_info.components["libzint"].requires.extend(["libpng::libpng", "zlib::zlib"])

        if self.options.with_qt:
            self.cpp_info.components["libqzint"].set_property("cmake_target_name", "Zint::QZint")
            self.cpp_info.components["libqzint"].type = "static-library"
            self.cpp_info.components["libqzint"].libs = ["QZint"]
            self.cpp_info.components["libqzint"].requires.extend([
                "libzint",
                "qt::qtGui",
            ])

        # Trick to only define Zint::QZint and Zint::Zint in CMakeDeps generator
        self.cpp_info.set_property("cmake_target_name", "Zint::QZint" if self.options.with_qt else "Zint::Zint")

