from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class EdlibConan(ConanFile):
    name = "edlib"
    description = "Lightweight, super fast C/C++ (& Python) library for " \
                  "sequence alignment using edit (Levenshtein) distance."
    topics = ("sequence-alignment", "edit-distance", "levehnstein-distance", "alignment-path")
    license = "MIT"
    homepage = "https://github.com/Martinsos/edlib"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return "11" if Version(self.version) < "1.2.7" else "14"

    @property
    def _minimum_compilers_version(self):
        return {
            "14": {
                "Visual Studio": "15",
                "msvc": "191",
                "gcc": "5",
                "clang": "5",
                "apple-clang": "5.1",
            },
        }.get(self._min_cppstd, {})

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["EDLIB_BUILD_EXAMPLES"] = False
        tc.variables["EDLIB_BUILD_UTILITIES"] = False
        if Version(self.version) >= "1.2.7":
            tc.variables["EDLIB_ENABLE_INSTALL"] = True
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0063"] = "NEW"
        # Needed because upstream CMakeLists overrides BUILD_SHARED_LIBS as a cache variable
        tc.cache_variables["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
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
        self.cpp_info.set_property("cmake_file_name", "edlib")
        self.cpp_info.set_property("cmake_target_name", "edlib::edlib")
        self.cpp_info.set_property("pkg_config_name", f"edlib-{Version(self.version).major}")
        self.cpp_info.libs = ["edlib"]
        if self.options.shared:
            self.cpp_info.defines = ["EDLIB_SHARED"]
        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("m")
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
