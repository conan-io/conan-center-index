from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class GeogramConan(ConanFile):
    name = "geogram"
    description = "a programming library with geometric algorithms"
    license = "BSD 3-Clause"
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

    short_paths = True

    @property
    def _min_cppstd(self):
        return 11

    # in case the project requires C++14/17/20/... the minimum compiler version should be listed
    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
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
        # src_folder must use the same source folder name the project
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_graphics:
            self.requires("xorg/system")
            self.requires("glfw/3.3.8")
            self.requires("imgui/cci.20230105+1.89.2.docking")

    def validate(self):
        # validate the minimum cpp standard supported. For C++ projects only
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )
        # in case it does not work in another configuration, it should validated here too
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.preprocessor_definitions["VORPALINE_BUILD_DYNAMIC"] = self.options.shared
        tc.variables["GEOGRAM_WITH_GRAPHICS"] = self.options.with_graphics
        tc.variables["GEOGRAM_LIB_ONLY"] = True
        # To use glfw from conan cache
        tc.variables["GEOGRAM_USE_SYSTEM_GLFW3"] = True
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

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

        self.cpp_info.components["geogram_num_3rdparty"].includedirs = ["include/geogram1"]
        self.cpp_info.components["geogram_num_3rdparty"].libs = ["geogram_num_3rdparty"]
        self.cpp_info.components["geogram_num_3rdparty"].set_property("cmake_target_name", "Geogram::geogram_num_3rdparty")

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
