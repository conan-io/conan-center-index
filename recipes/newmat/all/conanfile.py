from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, load, collect_libs, rmdir
import os

required_conan_version = ">=1.53.0"


class NewmatConan(ConanFile):
    name = "newmat"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://newmat.net"
    description = "Manipulate a variety of types of matrices using standard matrix operations."
    settings = "os", "compiler", "build_type", "arch"
    topics = ("newmat", "matrix")
    license = "MIT"
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
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate_build(self):
        if self.settings.os == "Windows" and self.options.shared == True:
            raise ConanInvalidConfiguration("Not working yet. Feel free to submit a fix in conan-center")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "nm11.htm", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "nm10.htm", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        if self.settings.os == "Windows":
            if self.options.shared == True:
                rmdir(self, os.path.join(self.package_folder, "lib"))
            else:
                rmdir(self, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]

        self.cpp_info.includedirs.append(os.path.join("include", "newmat"))

