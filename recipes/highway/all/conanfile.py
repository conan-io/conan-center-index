from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class HighwayConan(ConanFile):
    name = "highway"
    description = "Performance-portable, length-agnostic SIMD with runtime dispatch"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/highway"
    topics = ("simd", "neon", "avx", "sse",)
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_test": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_test": False,
    }

    @property
    def _min_cppstd(self):
        return "11"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if Version(self.version) < "0.16.0":
            del self.options.shared
            self.package_type = "static-library"
        elif self.options.shared:
            self.options.rm_safe("fPIC")
        if Version(self.version) < "1.0.6":
            del self.options.with_test

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["HWY_ENABLE_EXAMPLES"] = False
        tc.variables["HWY_ENABLE_TESTS"] = self.options.get_safe("with_test", False)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Honor fPIC option
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)", "")
        replace_in_file(self, cmakelists,
                              "set_property(TARGET hwy PROPERTY POSITION_INDEPENDENT_CODE ON)",
                              "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.components["hwy"].set_property("pkg_config_name", "libhwy")
        self.cpp_info.components["hwy"].libs = ["hwy"]
        if Version(self.version) >= "0.16.0":
            self.cpp_info.components["hwy"].defines.append(
                "HWY_SHARED_DEFINE" if self.options.shared else "HWY_STATIC_DEFINE"
            )
        if Version(self.version) >= "0.12.1":
            self.cpp_info.components["hwy_contrib"].set_property("pkg_config_name", "libhwy-contrib")
            self.cpp_info.components["hwy_contrib"].libs = ["hwy_contrib"]
            self.cpp_info.components["hwy_contrib"].requires = ["hwy"]
        if "0.15.0" <= Version(self.version) < "1.0.6" or (Version(self.version) >= "1.0.6" and self.options.with_test):
            self.cpp_info.components["hwy_test"].set_property("pkg_config_name", "libhwy-test")
            self.cpp_info.components["hwy_test"].libs = ["hwy_test"]
            self.cpp_info.components["hwy_test"].requires = ["hwy"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
