from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class RoaringConan(ConanFile):
    name = "roaring"
    description = "Portable Roaring bitmaps in C and C++"
    license = ("Apache-2.0", "MIT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/RoaringBitmap/CRoaring"
    topics = ("bitset", "compression", "index", "format")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_avx": [True, False],
        "with_avx512": [True, False],
        "with_neon": [True, False],
        "native_optimization": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_avx": True,
        "with_avx512": True,
        "with_neon": True,
        "native_optimization": False,
    }

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ("x86", "x86_64"):
            del self.options.with_avx
            del self.options.with_avx512
        if not str(self.settings.arch).startswith("arm"):
            del self.options.with_neon

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if self.settings.compiler == "apple-clang" and Version(self.settings.compiler.version) < "11":
            raise ConanInvalidConfiguration(
                f"{self.ref} requires at least apple-clang 11 to support runtime dispatching.",
                )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ROARING_DISABLE_AVX"] = not self.options.get_safe("with_avx", False)
        if "with_avx512" in self.options:
            tc.variables["ROARING_DISABLE_AVX512"] = not self.options.with_avx512
        tc.variables["ROARING_DISABLE_NEON"] = not self.options.get_safe("with_neon", False)
        tc.variables["ROARING_DISABLE_NATIVE"] = not self.options.native_optimization
        tc.variables["ROARING_BUILD_STATIC"] = not self.options.shared
        tc.variables["ENABLE_ROARING_TESTS"] = False
        # Relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "roaring")
        self.cpp_info.set_property("cmake_target_name", "roaring::roaring")
        self.cpp_info.set_property("pkg_config_name", "roaring")
        self.cpp_info.libs = ["roaring"]
