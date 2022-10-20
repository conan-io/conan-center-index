from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class Tinyxml2Conan(ConanFile):
    name = "tinyxml2"
    description = "Simple, small, efficient, C++ XML parser that can be " \
                  "easily integrated into other programs."
    license = "Zlib"
    topics = ("tinyxml2", "xml", "parser")
    homepage = "https://github.com/leethomason/tinyxml2"
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

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        if Version(self.version) < "8.1.0":
            # Relocatable shared lib on Macos
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        if Version(self.version) < "9.0.0":
            # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tinyxml2")
        self.cpp_info.set_property("cmake_target_name", "tinyxml2::tinyxml2")
        self.cpp_info.set_property("pkg_config_name", "tinyxml2")
        postfix = "d" if self.settings.build_type == "Debug" and Version(self.version) < "8.1.0" else ""
        self.cpp_info.libs = [f"tinyxml2{postfix}"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("TINYXML2_IMPORT")
