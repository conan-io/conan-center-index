from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, rmdir, save, load
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"


class NewmatConan(ConanFile):
    name = "newmat"
    description = "Manipulate a variety of types of matrices using standard matrix operations."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.robertnz.net/nm11.htm"
    topics = ("matrix")
    license = "LicenseRef-newmat"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_c_subscripts": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_c_subscripts": False,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
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
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} does not support dynamic library with msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SETUP_C_SUBSCRIPTS"] = self.options.with_c_subscripts
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def _extract_license(self):
        header = load(self, os.path.join(self.source_folder, "nm11.htm"))
        return header[header.find("I place no restrictions", 1) : header.find("report bugs to me.", 1) + 18]

    def package(self):
        cmake = CMake(self)
        cmake.install()
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        if self.settings.os == "Windows":
            rmdir(self, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["newmat"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]

        self.cpp_info.includedirs.append(os.path.join("include", "newmat"))
        if self.options.with_c_subscripts:
            self.cpp_info.defines.append("SETUP_C_SUBSCRIPTS")

