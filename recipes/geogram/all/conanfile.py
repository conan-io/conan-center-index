from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc
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
        "with_graphics": False,
    }
    
    package_type = "library"
    short_paths = True

    @property
    def _min_cppstd(self):
        return 11
    
    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
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
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def requirements(self):
        self.requires("zlib/[>=1.2.11 <2]")
        self.requires("libmeshb/7.80")
        self.requires("rply/1.1.4")
        self.requires("amgcl/1.4.4")

        if self.options.with_graphics:
            self.requires("xorg/system")
            self.requires("glfw/3.4")
            # See https://github.com/conan-io/conan-center-index/pull/25325
            self.requires("imgui/1.91.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.shared:
            tc.preprocessor_definitions["GEO_DYNAMIC_LIBS"] = None
        tc.variables["VORPALINE_BUILD_DYNAMIC"] = self.options.shared
        tc.variables["GEOGRAM_WITH_GRAPHICS"] = self.options.with_graphics
        tc.variables["GEOGRAM_LIB_ONLY"] = True
        tc.variables["GEOGRAM_WITH_LEGACY_NUMERICS"] = False
        tc.variables["GEOGRAM_WITH_HLBFGS"] = False
        tc.variables["GEOGRAM_WITH_TETGEN"] = False
        tc.variables["GEOGRAM_WITH_TRIANGLE"] = False
        tc.variables["GEOGRAM_WITH_LUA"] = False
        tc.variables["GEOGRAM_WITH_FPG"] = False
        # To use glfw from conan dependencies
        tc.variables["GEOGRAM_USE_SYSTEM_GLFW3"] = True
        tc.variables["GEOGRAM_WITH_GARGANTUA"] = False
        tc.variables["GEOGRAM_WITH_TBB"] = False
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Remove gitmodules dependencies
        rmdir(self, os.path.join(self.source_folder, "src/lib/third_party/glfw"))
        rmdir(self, os.path.join(self.source_folder, "src/lib/geogram/third_party/amgcl"))
        rmdir(self, os.path.join(self.source_folder, "src/lib/geogram/third_party/libMeshb"))
        rmdir(self, os.path.join(self.source_folder, "src/lib/geogram/third_party/rply"))
        rmdir(self, os.path.join(self.source_folder, "src/lib/geogram/third_party/zlib"))
        rmdir(self, os.path.join(self.source_folder, "src/lib/geogram_gfx/third_party/imgui"))
        # replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "add_subdirectory(src/lib/third_party)", "")
        # replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "add_subdirectory(doc)", "")
        # replace_in_file(self, os.path.join(self.source_folder, "src", "lib", "geogram", "CMakeLists.txt"), "add_subdirectory(third_party)", 
        #                 """
        #                 add_subdirectory(third_party)
                        
        #                 find_package(libMeshb REQUIRED CONFIG)
        #                 find_package(rply REQUIRED CONFIG)
        #                 find_package(amgcl REQUIRED CONFIG)
        #                 """)
        # replace_in_file(self, os.path.join(self.source_folder, "src", "lib", "geogram", "CMakeLists.txt"), "add_library(geogram ${SOURCES} $<TARGET_OBJECTS:geogram_third_party>)", 
        #                 """
        #                 add_library(geogram ${SOURCES} $<TARGET_OBJECTS:geogram_third_party>)

        #                 target_link_libraries(geogram libMeshb::Meshb.7)
        #                 target_link_libraries(geogram rply::rply)
        #                 target_link_libraries(geogram amgcl::amgcl)
        #                 """)

        # Rework cpp includes to works with libmeshb conan dependency
        # replace_in_file(self, os.path.join(self.source_folder, "src/lib/geogram/mesh/mesh_io.cpp"), "#include <geogram/third_party/libMeshb/sources/libmeshb7.h>", "#include <libmeshb7.h>")
        # replace_in_file(self, os.path.join(self.source_folder, "src/lib/geogram/mesh/mesh_io.cpp"), "#include <geogram/third_party/rply/rply.h>", "#include <rply.h>")

        # Disable cmake specific stuff in favor of CMakeDeps generated ones 
        # replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "include(cmake/geo_detect_platform.cmake)", "")
        # replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "include(cmake/geogram.cmake)", "include(cmake/utilities.cmake)")
        # replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), 'string(REGEX REPLACE "-[^-]+$" "" VORPALINE_OS ${VORPALINE_PLATFORM})', "")
        # replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), 'set(CPACK_SYSTEM_NAME ${VORPALINE_OS})', "")
        # replace_in_file(self, os.path.join(self.source_folder, "src/bin/fpg/CMakeLists.txt"), "vor_reset_warning_level()", "")
        # replace_in_file(self, os.path.join(self.source_folder, "src/lib/geogram/third_party/CMakeLists.txt"), "vor_reset_warning_level()", "")
        # replace_in_file(self, os.path.join(self.source_folder, "src/lib/geogram_gfx/third_party/CMakeLists.txt"), "vor_reset_warning_level()", "")
        # replace_in_file(self, os.path.join(self.source_folder, "src/lib/third_party/CMakeLists.txt"), "vor_reset_warning_level()", "")
        # replace_in_file(self, os.path.join(self.source_folder, "src/lib/third_party/numerics/CMakeLists.txt"), "vor_reset_warning_level()", "")

        # replace_in_file(self, os.path.join(self.source_folder, "cmake/geogram.cmake"), "if(NOT VORPALINE_PLATFORM)", "if(0)")
        # replace_in_file(self, os.path.join(self.source_folder, "cmake/geogram.cmake"), "include(${GEOGRAM_SOURCE_DIR}/cmake/platforms/${VORPALINE_PLATFORM}/config.cmake)", "")
        # # To disable rpath
        # replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "if(VORPALINE_BUILD_DYNAMIC)", "if(0)")

    def build(self):
        self._patch_sources()
        
        cmake = CMake(self)
        cmake.configure()
        # cmake.build()
        cmake.build(cli_args=["--verbose"])

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
            self.cpp_info.components["geogram_gfx"].set_property("cmake_target_name", "Geogram::geogram_gfx")

        # self.cpp_info.components["geogram_num_3rdparty"].includedirs = ["include/geogram1"]
        # self.cpp_info.components["geogram_num_3rdparty"].libs = ["geogram_num_3rdparty"]
        # self.cpp_info.components["geogram_num_3rdparty"].set_property("cmake_target_name", "Geogram::geogram_num_3rdparty")

        self.cpp_info.components["geogram"].includedirs = ["include/geogram1"]
        self.cpp_info.components["geogram"].libs = ["geogram"]
        self.cpp_info.components["geogram"].requires = ["zlib::zlib", "libmeshb::libmeshb", "rply::rply", "amgcl::amgcl"]
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
