from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"

class GeogramConan(ConanFile):
    name = "geogram"
    description = "A programming library with geometric algorithms"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/BrunoLevy/geogram"
    topics = ("graphics programming", "mesh generation", "geometry processing", "graphics libraries", "mesh processing")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_graphics": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_graphics": True,
    }
    
    package_type = "library"
    short_paths = True

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

    def requirements(self):
        if self.options.with_graphics:
            # self.requires("xorg/system")
            self.requires("glfw/3.3.8")
            # self.requires("imgui/cci.20230105+1.89.2.docking")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["VORPALINE_BUILD_DYNAMIC"] = self.options.shared
        tc.variables["GEOGRAM_WITH_GRAPHICS"] = self.options.with_graphics
        tc.variables["GEOGRAM_LIB_ONLY"] = False
        # To use glfw from conan cache
        tc.variables["GEOGRAM_USE_SYSTEM_GLFW3"] = True
        # tc.variables["GEOGRAM_SUB_BUILD"] = True
        tc.variables["GEOGRAM_WITH_LEGACY_NUMERICS"] = False
        
        tc.generate()
        
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.verbose = True
        cmake.build(cli_args=["--verbose"], build_tool_args=["-j 10"])
        # cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Geogram")

        if self.options.with_graphics:
            self.cpp_info.components["geogram_gfx"].includedirs = ["include/geogram1"]
            self.cpp_info.components["geogram_gfx"].libs = ["geogram_gfx"]
            self.cpp_info.components["geogram_gfx"].requires = ["geogram", "glfw::glfw"]
            self.cpp_info.components["geogram_gfx"].set_property("cmake_target_name", "Geogram::geogram")

        # self.cpp_info.components["geogram_num_3rdparty"].includedirs = ["include/geogram1"]
        # self.cpp_info.components["geogram_num_3rdparty"].libs = ["geogram_num_3rdparty"]
        # self.cpp_info.components["geogram_num_3rdparty"].set_property("cmake_target_name", "Geogram::geogram_num_3rdparty")

        self.cpp_info.components["geogram"].includedirs = ["include/geogram1"]
        self.cpp_info.components["geogram"].libs = ["geogram"]
        self.cpp_info.components["geogram"].set_property("cmake_target_name", "Geogram::geogram")
        if not self.options.shared:
            openmp_flags = []
            if is_msvc(self):
                openmp_flags = ["-openmp"]
            elif self.settings.compiler in ("gcc", "clang"):
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler == "apple-clang":
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]
            self.cpp_info.components["geogram"].sharedlinkflags = openmp_flags
            self.cpp_info.components["geogram"].exelinkflags = openmp_flags

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")
