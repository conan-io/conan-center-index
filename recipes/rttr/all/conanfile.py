from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, get, replace_in_file, rm, rmdir
import os

required_conan_version = ">=1.50.0"


class RTTRConan(ConanFile):
    name = "rttr"
    description = "Run Time Type Reflection library"
    topics = ("reflection", "rttr", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rttrorg/rttr"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_rtti": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_rtti": False,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_DOCUMENTATION"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_UNIT_TESTS"] = False
        tc.variables["BUILD_WITH_RTTI"] = self.options.with_rtti
        tc.variables["BUILD_PACKAGE"] = False
        tc.variables["BUILD_RTTR_DYNAMIC"] = self.options.shared
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # No warnings as errors
        for target in ["rttr_core", "rttr_core_lib", "rttr_core_s", "rttr_core_lib_s"]:
            replace_in_file(
                self,
                os.path.join(self.source_folder, "src", "rttr", "CMakeLists.txt"),
                f"set_compiler_warnings({target})",
                "",
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        cmake_target = "Core" if self.options.shared else "Core_Lib"
        self.cpp_info.set_property("cmake_file_name", "rttr")
        self.cpp_info.set_property("cmake_target_name", f"RTTR::{cmake_target}")
        # TODO: back to global scope in conan v2 once cmake_find_package* generators removed
        self.cpp_info.components["_rttr"].libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_rttr"].system_libs = ["dl", "pthread"]
        if self.options.shared:
            self.cpp_info.components["_rttr"].defines = ["RTTR_DLL"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "rttr"
        self.cpp_info.filenames["cmake_find_package_multi"] = "rttr"
        self.cpp_info.names["cmake_find_package"] = "RTTR"
        self.cpp_info.names["cmake_find_package_multi"] = "RTTR"
        self.cpp_info.components["_rttr"].names["cmake_find_package"] = cmake_target
        self.cpp_info.components["_rttr"].names["cmake_find_package_multi"] = cmake_target
        self.cpp_info.components["_rttr"].set_property("cmake_target_name", f"RTTR::{cmake_target}")
