from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get, apply_conandata_patches, export_conandata_patches, rename
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"

class DSPFiltersConan(ConanFile):
    name = "dsp-filters"
    description = "Set of DSP filters"
    topics = ("dsp", "filters")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/vinniefalco/DSPFilters"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def validate(self):
        # in case it does not work in another configuration, it should validated here too
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "shared"))
        cmake.build()

    def package(self):
        copy(self, "lib*", src=os.path.join(self.build_folder, "DSPFilters"), dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "DSPFilters.lib", src=os.path.join(self.build_folder, "DSPFilters", f"{self.settings.build_type}"), dst=os.path.join(self.package_folder, "lib"), keep_path=False)

        copy(self, "*.h", src=os.path.join(self.source_folder, "shared", "DSPFilters", "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "README.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rename(self, src=os.path.join(self.package_folder, "licenses", "README.md"), dst=os.path.join(self.package_folder, "licenses", "license"))

    def package_info(self):
        self.cpp_info.libs = ["DSPFilters"]

        if self.settings.os in ["Linux", "FreeBSD", "Neutrino"]:
            self.cpp_info.system_libs.extend(["m"])
