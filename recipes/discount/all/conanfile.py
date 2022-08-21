from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
import os

required_conan_version = ">=1.50.0"


class DiscountConan(ConanFile):
    name = "discount"
    description = "DISCOUNT is a implementation of John Gruber & Aaron Swartz's Markdown markup language."
    license = "BSD-3-Clause"
    topics = ("discount", "markdown")
    homepage = "http://www.pell.portland.or.us/~orc/Code/discount"
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
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("discount doesn't support cross-build yet")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DISCOUNT_MAKE_INSTALL"] = True
        tc.variables["DISCOUNT_INSTALL_SAMPLES"] = False
        tc.variables["DISCOUNT_ONLY_LIBRARY"] = True
        # For shared msvc
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        # Relocatable shared lib on Macos
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "cmake"))
        cmake.build()

    def package(self):
        copy(self, "COPYRIGHT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "discount")
        self.cpp_info.set_property("cmake_target_name", "discount::libmarkdown")
        self.cpp_info.set_property("pkg_config_name", "libmarkdown")
        # TODO: back to global scope in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.components["_discount"].libs = ["markdown"]

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "discount"
        self.cpp_info.names["cmake_find_package_multi"] = "discount"
        self.cpp_info.names["pkg_config"] = "libmarkdown"
        self.cpp_info.components["_discount"].names["cmake_find_package"] = "libmarkdown"
        self.cpp_info.components["_discount"].names["cmake_find_package_multi"] = "libmarkdown"
        self.cpp_info.components["_discount"].set_property("pkg_config_name", "libmarkdown")
