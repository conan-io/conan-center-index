from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file,  rmdir
import os

required_conan_version = ">=1.53.0"

class LibmeshbConan(ConanFile):
    name = "libmeshb"
    description = "A library to handle the *.meshb file format."
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/LoicMarechal/libMeshb"
    topics = ("3d", "mesh", "geometry")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_gmf_asio": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_gmf_asio": False
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_gmf_asio
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def configure(self):
        # Windows shared build doesn't seems supported because code doesn't include dllexport
        # See https://www.kitware.com/create-dlls-on-windows-without-declspec-using-new-cmake-export-all-feature/
        if self.settings.os == "Windows":
            del self.options.shared
            self.package_type = "static-library"
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_GMF_AIO"] = self.options.get_safe("with_gmf_asio", False)
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "add_subdirectory (examples)", "")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "install (FILES LICENSE.txt copyright.txt DESTINATION share/libMeshb)", "")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "install (DIRECTORY sample_meshes DESTINATION share/libMeshb)", "")
        replace_in_file(self, os.path.join(self.source_folder, "sources/CMakeLists.txt"), "install(DIRECTORY ${CMAKE_Fortran_MODULE_DIRECTORY}/ DESTINATION include)", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libMeshb")
        self.cpp_info.set_property("cmake_target_name", "libMeshb::Meshb.7")
        self.cpp_info.libs = ["Meshb.7"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("rt")
            self.cpp_info.system_libs.append("m")