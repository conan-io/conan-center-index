from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class Clipper2Conan(ConanFile):
    name = "clipper2"
    description = " A Polygon Clipping and Offsetting library in C++"
    license = "BSL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/AngusJohnson/Clipper2"
    topics = ("geometry", "polygon", "clipping")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "usingz": ["ON", "OFF", "ONLY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "usingz": "ON",
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
            "Visual Studio": "16",
            "msvc": "192",
        }

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
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root = Version(self.version) >= "1.2.3")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["CLIPPER2_UTILS"] = False
        tc.variables["CLIPPER2_EXAMPLES"] = False
        tc.variables["CLIPPER2_TESTS"] = False
        tc.variables["CLIPPER2_USINGZ"] = self.options.usingz
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "CPP"))
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        if self.options.usingz != "ONLY":
            self.cpp_info.components["clipper2"].set_property("cmake_target_name", "Clipper2::clipper2")
            self.cpp_info.components["clipper2"].set_property("pkg_config_name", "Clipper2")
            self.cpp_info.components["clipper2"].libs = ["Clipper2"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["clipper2"].system_libs.append("m")

        if self.options.usingz != "OFF":
            self.cpp_info.components["clipper2z"].set_property("cmake_target_name", "Clipper2::clipper2z")
            self.cpp_info.components["clipper2z"].set_property("pkg_config_name", "Clipper2Z")
            self.cpp_info.components["clipper2z"].libs = ["Clipper2Z"]
            self.cpp_info.components["clipper2z"].defines.append("USINGZ")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["clipper2z"].system_libs.append("m")
