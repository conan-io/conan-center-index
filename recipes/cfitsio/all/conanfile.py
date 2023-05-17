from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import glob
import os

required_conan_version = ">=1.54.0"


class CfitsioConan(ConanFile):
    name = "cfitsio"
    description = "C library for reading and writing data files in FITS " \
                  "(Flexible Image Transport System) data format"
    license = "ISC"
    topics = ("fits", "image", "nasa", "astronomy", "astrophysics", "space")
    homepage = "https://heasarc.gsfc.nasa.gov/fitsio/"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [True, False],
        "simd_intrinsics": [None, "sse2", "ssse3"],
        "with_bzip2": [True, False],
        "with_curl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": False,
        "simd_intrinsics": None,
        "with_bzip2": False,
        "with_curl": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_curl
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.simd_intrinsics

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zlib/1.2.13")
        if self.options.threadsafe and self.settings.os == "Windows" and \
           self.settings.compiler.get_safe("threads") != "posix":
            self.requires("pthreads4w/3.0.0")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.get_safe("with_curl"):
            self.requires("libcurl/8.0.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["USE_PTHREADS"] = self.options.threadsafe
        if Version(self.version) >= "4.1.0":
            tc.variables["USE_SSE2"] = self.options.get_safe("simd_intrinsics") == "sse2"
            tc.variables["USE_SSSE3"] = self.options.get_safe("simd_intrinsics") == "ssse3"
            tc.variables["USE_BZIP2"] = self.options.with_bzip2
        else:
            tc.variables["CFITSIO_USE_SSE2"] = self.options.get_safe("simd_intrinsics") == "sse2"
            tc.variables["CFITSIO_USE_SSSE3"] = self.options.get_safe("simd_intrinsics") == "ssse3"
            tc.variables["CFITSIO_USE_BZIP2"] = self.options.with_bzip2
        if Version(self.version) >= "4.0.0":
            tc.variables["USE_CURL"] = self.options.get_safe("with_curl", False)
            tc.variables["TESTS"] = False
            tc.variables["UTILS"] = False
        else:
            tc.variables["UseCurl"] = self.options.get_safe("with_curl", False)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if Version(self.version) < "4.0.0":
            # Remove embedded zlib files
            for zlib_file in glob.glob(os.path.join(self.source_folder, "zlib", "*")):
                if not zlib_file.endswith(("zcompress.c", "zuncompress.c")):
                    os.remove(zlib_file)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "License.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", f"cfitsio-{self.version}"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cfitsio")
        self.cpp_info.set_property("cmake_target_name", "cfitsio::cfitsio")
        self.cpp_info.set_property("pkg_config_name", "cfitsio")
        self.cpp_info.libs = ["cfitsio"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")
