import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class PdfiumConan(ConanFile):
    name = "pdfium"
    description = "PDF generation and rendering library."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://opensource.google/projects/pdfium"
    topics = ("generate", "generation", "rendering", "pdf", "document", "print")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libjpeg": "libjpeg",
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("freetype/2.13.2")
        self.requires("icu/74.1")
        self.requires("lcms/2.14")
        self.requires("openjpeg/2.5.0")
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 14)
        minimum_compiler_versions = {
            "gcc": "8",
            "msvc": "191",
            "Visual Studio": "15",
        }
        min_compiler_version = minimum_compiler_versions.get(str(self.settings.compiler))
        if min_compiler_version and Version(self.settings.compiler.version) < min_compiler_version:
            raise ConanInvalidConfiguration(
                f"pdfium needs at least compiler version {min_compiler_version}"
            )

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["pdfium-cmake"],
            destination=os.path.join(self.source_folder, "pdfium-cmake"), strip_root=True)
        get(self, **self.conan_data["sources"][self.version]["pdfium"],
            destination=self.source_folder)
        get(self, **self.conan_data["sources"][self.version]["trace_event"],
            destination=os.path.join(self.source_folder, "base", "trace_event", "common"))
        get(self, **self.conan_data["sources"][self.version]["chromium_build"],
            destination=os.path.join(self.source_folder, "build"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PDFIUM_ROOT"] = self.source_folder.replace("\\", "/")
        tc.variables["PDF_LIBJPEG_TURBO"] = self.options.with_libjpeg == "libjpeg-turbo"
        tc.variables["PDF_ENABLE_XFA"] = False  # TODO: pdfium-cmake needs updating
        tc.variables["PDF_ENABLE_V8"] = False  # TODO: requires v8
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join("pdfium-cmake", "cmake"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["pdfium"]
        if is_apple_os(self):
            self.cpp_info.frameworks.extend(["AppKit", "CoreFoundation", "CoreGraphics"])

        stdcpp = stdcpp_library(self)
        if stdcpp:
            self.cpp_info.system_libs.append(stdcpp)
