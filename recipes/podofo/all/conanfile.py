from conan import ConanFile
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class PodofoConan(ConanFile):
    name = "podofo"
    license = "GPL-3.0", "LGPL-3.0"
    homepage = "http://podofo.sourceforge.net"
    url = "https://github.com/conan-io/conan-center-index"
    description = "PoDoFo is a library to work with the PDF file format."
    topics = ("pdf")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [True, False],
        "with_openssl": [True, False],
        "with_libidn": [True, False],
        "with_jpeg": [True, False],
        "with_tiff": [True, False],
        "with_png": [True, False],
        "with_unistring": [True, False],
        "with_tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": True,
        "with_openssl": True,
        "with_libidn": True,
        "with_jpeg": True,
        "with_tiff": True,
        "with_png": True,
        "with_unistring": True,
        "with_tools": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if is_msvc(self):
            # libunistring recipe raises for Visual Studio
            # TODO: Enable again when fixed?
            self.options.with_unistring = False

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("freetype/2.13.0")
        self.requires("zlib/[>=1.2.11 <2]")
        if self.settings.os != "Windows":
            self.requires("fontconfig/2.14.2")
        if self.options.with_openssl:
            self.requires("openssl/1.1.1u")
        if self.options.with_libidn:
            self.requires("libidn/1.36")
        if self.options.with_jpeg:
            self.requires("libjpeg/9e")
        if self.options.with_tiff:
            self.requires("libtiff/4.5.1")
        if self.options.with_png:
            self.requires("libpng/1.6.40")
        if self.options.with_unistring:
            self.requires("libunistring/0.9.10")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd") and Version(self.version) >= "0.9.7":
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PODOFO_BUILD_TOOLS"] = self.options.with_tools
        tc.variables["PODOFO_BUILD_SHARED"] = self.options.shared
        tc.variables["PODOFO_BUILD_STATIC"] = not self.options.shared
        if not self.options.threadsafe:
            tc.variables["PODOFO_NO_MULTITHREAD"] = True
        if Version(self.version) >= "0.9.7" and not valid_min_cppstd(self, 11):
            tc.cache_variables["CMAKE_CXX_STANDARD"] = 11

        # To install relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"

        # Custom CMake options injected in our patch, required to ensure reproducible builds
        tc.variables["PODOFO_WITH_OPENSSL"] = self.options.with_openssl
        tc.variables["PODOFO_WITH_LIBIDN"] = self.options.with_libidn
        tc.variables["PODOFO_WITH_LIBJPEG"] = self.options.with_jpeg
        tc.variables["PODOFO_WITH_TIFF"] = self.options.with_tiff
        tc.variables["PODOFO_WITH_PNG"] = self.options.with_png
        tc.variables["PODOFO_WITH_UNISTRING"] = self.options.with_unistring
        tc.variables["PODOFO_HAVE_OPENSSL_1_1"] = Version(self.dependencies["openssl"].ref.version) >= "1.1"
        if self.options.with_openssl and ("no_rc4" in self.dependencies["openssl"].options):
            tc.variables["PODOFO_HAVE_OPENSSL_NO_RC4"] = self.dependencies["openssl"].options.no_rc4
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

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

    def package_info(self):
        podofo_version = Version(self.version)
        pkg_config_name = f"libpodofo-{podofo_version.major}" if podofo_version < "0.9.7" else "libpodofo"
        self.cpp_info.set_property("pkg_config_name", pkg_config_name)
        self.cpp_info.libs = ["podofo"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("USING_SHARED_PODOFO")
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.threadsafe:
            self.cpp_info.system_libs = ["pthread"]
