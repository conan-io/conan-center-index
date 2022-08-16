from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.47.0"


class GiflibConan(ConanFile):
    name = "giflib"
    description = "A library and utilities for reading and writing GIF images."
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "http://giflib.sourceforge.net"
    topics = ("giflib", "image", "multimedia", "format", "graphics")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "utils" : [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "utils" : True,
    }

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if is_msvc(self):
            self.requires("getopt-for-visual-studio/20200201")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GIFLIB_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["UTILS"] = self.options.utils
        tc.generate()

        if is_msvc(self):
            cd = CMakeDeps(self)
            cd.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "GIF")
        self.cpp_info.set_property("cmake_target_name", "GIF::GIF")

        self.cpp_info.names["cmake_find_package"] = "GIF"
        self.cpp_info.names["cmake_find_package_multi"] = "GIF"

        self.cpp_info.libs = ["gif"]
        if is_msvc(self):
            self.cpp_info.defines.append("USE_GIF_DLL" if self.options.shared else "USE_GIF_LIB")

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
