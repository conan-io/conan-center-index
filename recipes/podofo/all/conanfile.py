from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
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
        "threadsafe": [True, False],
        "with_openssl": [True, False],
        "with_libidn": [True, False],
        "with_jpeg": [True, False],
        "with_tiff": [True, False],
        "with_png": [True, False],
        "with_unistring": [True, False],
        "with_tools": [True, False],
        "with_lib_only": [True, False],
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
        "with_lib_only": True,
    }

    @property
    def _with_openssl(self):
        return self.options.get_safe("with_openssl", True)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if Version(self.version) >= "0.10.4":
            # Required in newer versions
            del self.options.with_openssl
        else:
            # Not available in older versions
            del self.options.with_lib_only

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
        if Version(self.version) >= "0.10.4":
            self.requires("libxml2/[>=2.12.5 <3]")
        if self.settings.os != "Windows":
            self.requires("fontconfig/2.15.0")
        if self._with_openssl:
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

    def build_requirements(self):
        if Version(self.version) >= "0.10.4":
            self.tool_requires("cmake/[>=3.16 <4]")

    def validate(self):
        if Version(self.version) >= "0.10.4":
            check_min_cppstd(self, 17)
        else:
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PODOFO_BUILD_TOOLS"] = self.options.with_tools
        if self.options.get_safe("with_lib_only"):
            tc.variables["PODOFO_BUILD_LIB_ONLY"] = self.options.with_lib_only
        if Version(self.version) < "0.10.0":
            # _STATIC controls the shared/static build type
            tc.variables["PODOFO_BUILD_SHARED"] = self.options.shared
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        tc.variables["PODOFO_BUILD_STATIC"] = not self.options.shared
        if not self.options.threadsafe:
            tc.variables["PODOFO_NO_MULTITHREAD"] = True

        # To install relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"

        # Custom CMake options injected in our patch, required to ensure reproducible builds
        tc.variables["PODOFO_WITH_OPENSSL"] = self._with_openssl
        tc.variables["PODOFO_WITH_LIBIDN"] = self.options.with_libidn
        tc.variables["PODOFO_WITH_LIBJPEG"] = self.options.with_jpeg
        tc.variables["PODOFO_WITH_TIFF"] = self.options.with_tiff
        tc.variables["PODOFO_WITH_PNG"] = self.options.with_png
        tc.variables["PODOFO_WITH_UNISTRING"] = self.options.with_unistring

        if self._with_openssl:
            tc.variables["PODOFO_HAVE_OPENSSL_1_1"] = self.dependencies["openssl"].ref.version >= "1.1"
            if self._with_openssl and ("no_rc4" in self.dependencies["openssl"].options):
                tc.variables["PODOFO_HAVE_OPENSSL_NO_RC4"] = self.dependencies["openssl"].options.no_rc4

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
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libpodofo")
        if Version(self.version) < "0.10.0":
            self.cpp_info.libs = ["podofo"]
            if self.settings.os == "Windows" and self.options.shared:
                self.cpp_info.defines.append("USING_SHARED_PODOFO")
        else:
            if not self.options.shared:
                self.cpp_info.libs = ["podofo", "podofo_private"]
                self.cpp_info.defines.append("PODOFO_STATIC")
            else:
                self.cpp_info.libs = ["podofo"]
                self.cpp_info.defines.append("PODOFO_SHARED")

        if self.settings.os in ["Linux", "FreeBSD"] and self.options.threadsafe:
            self.cpp_info.system_libs = ["pthread"]
