from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class LibxlsxwriterConan(ConanFile):
    name = "libxlsxwriter"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jmcnamara/libxlsxwriter"
    topics = ("excel", "xlsx")
    description = "A C library for creating Excel XLSX files"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tmpfile": [True, False],
        "md5": [False, "openwall", "openssl"],
        "fmemopen": [True, False],
        "dtoa": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "tmpfile": False,
        "md5": "openwall",
        "fmemopen": False,
        "dtoa": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.fmemopen

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("minizip/1.2.13")
        self.requires("zlib/[>=1.2.11 <2]")
        if self.options.md5 == "openssl":
            self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        if Version(self.version) < "1.0.6" and self.info.options.md5 == "openssl":
            raise ConanInvalidConfiguration(f"{self.name}:md5=openssl is not suppported in {self.ref}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["USE_SYSTEM_MINIZIP"] = True
        tc.variables["USE_STANDARD_TMPFILE"] = self.options.tmpfile
        tc.variables["USE_NO_MD5"] = not bool(self.options.md5)
        if Version(self.version) >= "1.0.6":
            tc.variables["USE_OPENSSL_MD5"] = self.options.md5 == "openssl"
        tc.variables["USE_FMEMOPEN"] = self.options.get_safe("fmemopen", False)
        tc.variables["USE_DTOA_LIBRARY"] = self.options.dtoa
        if is_msvc(self):
            tc.variables["USE_STATIC_MSVC_RUNTIME"] = is_msvc_static_runtime(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "License.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "xlsxwriter")
        self.cpp_info.libs = ["xlsxwriter"]
