import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=2.0"


class PodofoConan(ConanFile):
    name = "podofo"
    license = "GPL-3.0", "LGPL-3.0"
    homepage = "http://podofo.sourceforge.net"
    url = "https://github.com/conan-io/conan-center-index"
    description = "PoDoFo is a library to work with the PDF file format."
    topics = ("pdf")

    package_type = "library"
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
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if is_msvc(self):
            # libunistring recipe raises for Visual Studio
            # TODO: Enable again when fixed?
            self.options.with_unistring = False
        if Version(self.version) >= "0.10":
            del self.options.with_openssl

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # None of the dependencies are used in public headers
        self.requires("freetype/2.13.2")
        self.requires("zlib/[>=1.2.11 <2]")
        if Version(self.version) >= "0.10":
            self.requires("libxml2/2.11.5")  # 2.12+ has minor incompatibilities
        if self.settings.os != "Windows":
            self.requires("fontconfig/2.15.0")
        if self.options.get_safe("with_openssl", True):
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_libidn:
            self.requires("libidn/1.36")
        if self.options.with_jpeg:
            self.requires("libjpeg/9e")
        if self.options.with_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_unistring:
            self.requires("libunistring/0.9.10")

    def validate(self):
        if Version(self.version) >= "0.10":
            check_min_cppstd(self, 17)
        else:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        if Version(self.version) >= "0.10":
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "(PoDoFo)",
                            "(PoDoFo)\n\ninclude(conan_deps.cmake)")
            # TODO: also fix libxml2 v2.12.x incompatibilities and submit a patch
            replace_in_file(self, os.path.join(self.source_folder, "src/podofo/private/XmlUtils.h"),
                            "#include <libxml/tree.h>",
                            "#include <libxml/tree.h>\n#include <libxml/xmlerror.h>")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PODOFO_BUILD_STATIC"] = not self.options.shared
        if Version(self.version) < "0.10":
            tc.variables["PODOFO_BUILD_SHARED"] = self.options.shared
        tc.variables["PODOFO_BUILD_TOOLS"] = self.options.with_tools
        tc.variables["PODOFO_BUILD_TEST"] = False
        tc.variables["PODOFO_BUILD_EXAMPLES"] = False
        if not self.options.threadsafe:
            tc.variables["PODOFO_NO_MULTITHREAD"] = True
        if Version(self.version) >= "0.9.7" and not valid_min_cppstd(self, 11):
            tc.cache_variables["CMAKE_CXX_STANDARD"] = 11

        # To install relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"

        # Custom CMake options injected in our patch, required to ensure reproducible builds
        tc.variables["WITH_ZLIB"] = True
        tc.variables["WITH_FREETYPE"] = True
        tc.variables["WITH_FONTCONFIG"] = self.settings.os != "Windows"
        tc.variables["WITH_OPENSSL"] = self.options.get_safe("with_openssl", True)
        tc.variables["WITH_LIBIDN"] = self.options.with_libidn
        tc.variables["WITH_LIBXML2"] = Version(self.version) >= "0.10"
        tc.variables["WITH_JPEG"] = self.options.with_jpeg
        tc.variables["WITH_LIBJPEG"] = self.options.with_jpeg
        tc.variables["WITH_TIFF"] = self.options.with_tiff
        tc.variables["WITH_PNG"] = self.options.with_png
        tc.variables["WITH_UNISTRING"] = self.options.with_unistring
        tc.variables["PODOFO_HAVE_OPENSSL_1_1"] = Version(self.dependencies["openssl"].ref.version) >= "1.1"
        if self.options.get_safe("with_openssl", True) and ("no_rc4" in self.dependencies["openssl"].options):
            tc.variables["PODOFO_HAVE_OPENSSL_NO_RC4"] = self.dependencies["openssl"].options.no_rc4
        tc.variables["PODOFO_V10"] = Version(self.version) >= "0.10"
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

    def package_info(self):
        podofo_version = Version(self.version)
        pkg_config_name = f"libpodofo-{podofo_version.major}" if podofo_version < "0.9.7" else "libpodofo"
        self.cpp_info.set_property("pkg_config_name", pkg_config_name)
        self.cpp_info.libs = ["podofo"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("USING_SHARED_PODOFO")
        if self.settings.os in ["Linux", "FreeBSD"] and self.options.threadsafe:
            self.cpp_info.system_libs = ["pthread"]
