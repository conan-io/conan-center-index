from conan import ConanFile
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    load,
    save,
)
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"


class QrCodeGeneratorConan(ConanFile):
    name = "qr-code-generator"
    description = "High-quality QR Code generator library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nayuki/QR-Code-generator"
    topics = ("qr", "qr-code", "qr-generator")
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

    def export_sources(self):
        copy(
            self,
            "CMakeLists.txt",
            src=self.recipe_folder,
            dst=self.export_sources_folder,
        )
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(
            self,
            **self.conan_data["sources"][self.version],
            destination=self.source_folder,
            strip_root=True
        )

    def generate(self):
        tc = CMakeToolchain(self)
        if self.settings.os == "Windows" and self.options.shared:
            tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        if not valid_min_cppstd(self, self._min_cppstd):
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def _extract_license(self):
        header_name = (
            "QrCode.hpp" if Version(self.version) < "1.7.0" else "qrcodegen.hpp"
        )
        header = load(self, os.path.join(self.source_folder, "cpp", header_name))
        license_contents = header[2 : header.find("*/", 1)]
        return license_contents

    def package(self):
        save(
            self,
            os.path.join(self.package_folder, "licenses", "LICENSE"),
            self._extract_license(),
        )
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["qrcodegencpp"].set_property("cmake_target_name", "qr-code-generator::qrcodegencpp")
        self.cpp_info.components["qrcodegencpp"].libs = ["qrcodegen" if Version(self.version) < "1.7.0" else "qrcodegencpp"]
        self.cpp_info.components["qrcodegenc"].set_property("cmake_target_name", "qr-code-generator::qrcodegenc")
        self.cpp_info.components["qrcodegenc"].libs = ["qrcodegenc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
