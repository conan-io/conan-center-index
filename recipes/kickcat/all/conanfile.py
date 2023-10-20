from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import get, copy
from conan.tools.scm import Version
import os

required_conan_version = ">=1.55"


class KickCATRecipe(ConanFile):
    name = "kickcat"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Siviuze/KickCAT"
    description = "Thin EtherCAT stack designed to be embedded in a more complex software and with efficiency in mind"
    license = "CeCILL-C"
    topics = ("ethercat")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                f"{self.ref} is not supported on {self.settings.os}.")

        if self.settings.compiler != "gcc":
            raise ConanInvalidConfiguration(
                f"{self.ref} is not supported on {self.settings.compiler}.")

        if self.settings.compiler == 'gcc' and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration("Building requires GCC >= 7")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_UNIT_TESTS"] = "OFF"
        tc.cache_variables["BUILD_EXAMPLES"] = "OFF"
        tc.cache_variables["BUILD_SIMULATION"] = "OFF"
        tc.cache_variables["BUILD_TOOLS"] = "OFF"
        tc.cache_variables["DEBUG"] = "OFF"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*.h", os.path.join(self.source_folder, "include"),
             os.path.join(self.package_folder, "include"))
        copy(self, "*.a", self.build_folder,
             os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.so", self.build_folder,
             os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "LICENSE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["kickcat"]
