from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, rm
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class PodofoConan(ConanFile):
    name = "podofo"
    license = "GPL-3.0", "LGPL-3.0"
    homepage = "http://podofo.sourceforge.net"
    url = "https://github.com/conan-io/conan-center-index"
    description = "PoDoFo is a library to work with the PDF file format."
    topics = ("pdf",)
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libidn": [True, False],
        "with_jpeg": [False, "libjpeg", "libjpeg-turbo", "mozjpeg"],
        "with_tiff": [True, False],
        "with_png": [True, False],
        "with_unistring": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libidn": True,
        "with_jpeg": "libjpeg",
        "with_tiff": True,
        "with_png": True,
        "with_unistring": True,
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
        self.requires("freetype/2.13.2")
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("libxml2/[>=2.12.5 <3]")
        self.requires("openssl/[>=1.1 <4]")

        # Unvendor 3rd party libraries
        self.requires("fmt/[>=11.0.2]")
        self.requires("date/3.0.4")
        self.requires("fast_float/6.1.0")
        self.requires("tcb-span/cci.20220616", transitive_headers=True)
        if Version(self.version) < "1.0.3":
            self.requires("utfcpp/[<4]")
        else:
            self.requires("utfcpp/[>=4.0.6]")
            self.requires("utf8proc/2.9.0")

        # Optional dependencies
        if self.settings.os != "Windows":
            self.requires("fontconfig/2.15.0")
        if self.options.with_libidn:
            self.requires("libidn/1.36")

        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/[>=9e]")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/[>=3.0.2 <4]")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/[>=4.1.5 <5]")

        if self.options.with_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_unistring:
            self.requires("libunistring/0.9.10")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)
        # Unvendor 3rd party libraries
        libraries_to_unvendor = ["fmt", "date", "utf8cpp", "tclap"]
        if Version(self.version) >= "1.0.3":
            libraries_to_unvendor.append("utf8proc")
            rm(self, "span.hpp", os.path.join(self.source_folder, "src", "podofo", "3rdparty"))
        else:
            rm(self, "span.hpp", os.path.join(self.source_folder, "src", "podofo", "auxiliary"))
        for vendor_library in libraries_to_unvendor:
            rmdir(self, os.path.join(self.source_folder, "3rdparty", vendor_library))
        # Remove single header fast_float to use the conan package
        rm(self, "fast_float.h", os.path.join(self.source_folder, "3rdparty"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["PODOFO_BUILD_TEST"] = False
        tc.cache_variables["PODOFO_BUILD_EXAMPLES"] = False
        tc.cache_variables["PODOFO_BUILD_STATIC"] = not self.options.shared
        tc.variables["PODOFO_HAVE_OPENSSL_NO_RC4"] = self.dependencies["openssl"].options.get_safe("no_rc4", False)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libpodofo")
        if not self.options.shared:
            self.cpp_info.libs = ["podofo", "podofo_private"]
            self.cpp_info.defines.append("PODOFO_STATIC")
            if Version(self.version) >= "1.0.3":
                # This is a private library which podofo links against itself.
                # This library is always built statically. When podofo is built as shared,
                # it is embedded inside the podofo shared library.
                self.cpp_info.libs.append("podofo_3rdparty")
        else:
            self.cpp_info.libs = ["podofo"]
            self.cpp_info.defines.append("PODOFO_SHARED")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]

