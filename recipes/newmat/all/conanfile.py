from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, copy, get, load, collect_libs, rm, rmdir
import os

required_conan_version = ">=1.53.0"


class NewmatConan(ConanFile):
    name = "newmat"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://newmat.net"
    description = "Manipulate a variety of types of matrices using standard matrix operations."
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["CMakeLists.txt", "newmat11.patch", "newmat6.cpp.patch"]
    topics = ("newmat", "matrix")
    license = "GPLv3"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

#    @property
#    def _is_mingw(self):
#        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

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

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "newmat"))

