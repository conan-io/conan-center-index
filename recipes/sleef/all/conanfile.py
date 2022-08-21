from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
import os

required_conan_version = ">=1.47.0"


class SleefConan(ConanFile):
    name = "sleef"
    description = "SLEEF is a library that implements vectorized versions " \
                  "of C standard math functions."
    license = "BSL-1.0"
    topics = ("conan", "sleef", "vectorization", "simd")
    homepage = "https://sleef.org"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    short_paths = True

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("shared sleef not supported on Windows, it produces runtime errors")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_STATIC_TEST_BINS"] = False
        tc.variables["ENABLE_LTO"] = False
        tc.variables["BUILD_LIBM"] = True
        tc.variables["BUILD_DFT"] = False
        tc.variables["BUILD_QUAD"] = False
        tc.variables["BUILD_GNUABI_LIBS"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_INLINE_HEADERS"] = False
        tc.variables["SLEEF_TEST_ALL_IUT"] = False
        tc.variables["SLEEF_SHOW_CONFIG"] = True
        tc.variables["SLEEF_SHOW_ERROR_LOG"] = False
        tc.variables["ENFORCE_TESTER"] = False
        tc.variables["ENFORCE_TESTER3"] = False
        tc.variables["ENABLE_ALTDIV"] = False
        tc.variables["ENABLE_ALTSQRT"] = False
        tc.variables["DISABLE_FFTW"] = True
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
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "sleef")
        self.cpp_info.libs = ["sleef"]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines = ["SLEEF_STATIC_LIBS"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
