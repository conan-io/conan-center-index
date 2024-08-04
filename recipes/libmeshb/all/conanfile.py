from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc
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
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")
        
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # To support shared lib (DLL) on Windows
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["WITH_GMF_AIO"] = self.settings.os in ["Linux", "FreeBSD"]
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
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