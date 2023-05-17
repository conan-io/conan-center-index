from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"


class EntityXConan(ConanFile):
    name = "entityx"
    description = (
        "EntityX is an EC system that uses C++11 features to provide type-safe "
        "component management, event delivery, etc."
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alecthomas/entityx/"
    topics = ("entity", "c++11", "type-safe", "component")
    license = "MIT"

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
            check_min_cppstd(self, 11)
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration("entityx shared library does not export all symbols with Visual Studio")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENTITYX_BUILD_SHARED"] = self.options.shared
        tc.variables["ENTITYX_BUILD_TESTING"] = False
        tc.variables["ENTITYX_RUN_BENCHMARKS"] = False
        # Relocatable shared lib on macOS
        tc.variables["CMAKE_MACOSX_RPATH"] = True
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "entityx")
        suffix = "-d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"entityx{suffix}"]
