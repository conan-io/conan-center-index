from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get
import os

required_conan_version = ">=1.46.0"


class LibsquishConan(ConanFile):
    name = "libsquish"
    description = "The libSquish library compresses images with the DXT " \
                  "standard (also known as S3TC)."
    license = "MIT"
    topics = ("libsquish", "image", "compression", "dxt", "s3tc")
    homepage = "https://sourceforge.net/projects/libsquish"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "openmp": [True, False],
        "sse2_intrinsics": [True, False],
        "altivec_intrinsics": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "openmp": False,
        "sse2_intrinsics": False,
        "altivec_intrinsics": False,
    }

    @property
    def _sse2_compliant_archs(self):
        return ["x86", "x86_64"]

    @property
    def _altivec_compliant_archs(self):
        return ["ppc32be", "ppc32", "ppc64le", "ppc64"]

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in self._sse2_compliant_archs:
            del self.options.sse2_intrinsics
        if self.settings.arch not in self._altivec_compliant_archs:
            del self.options.altivec_intrinsics

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SQUISH_WITH_OPENMP"] = self.options.openmp
        tc.variables["BUILD_SQUISH_WITH_SSE2"] = self.options.get_safe("sse2_intrinsics") or False
        tc.variables["BUILD_SQUISH_WITH_ALTIVEC"] = self.options.get_safe("altivec_intrinsics") or False
        tc.variables["BUILD_SQUISH_EXTRA"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
