import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rm, export_conandata_patches, apply_conandata_patches
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class METISConan(ConanFile):
    name = "metis"
    description = (
        "Set of serial programs for partitioning graphs, "
        "partitioning finite element meshes, and producing "
        "fill reducing orderings for sparse matrices"
    )
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KarypisLab/METIS"
    topics = ("karypislab", "graph", "partitioning-algorithms")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_64bit_types": [True, False],
        "enable_gkrand": [True, False],
        "enable_gkregex": [True, False],
        "with_openmp": [True, False],
        "with_pcre": [True, False],
        "with_valgrind": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_64bit_types": False,
        "enable_gkrand": False,
        "enable_gkregex": False,
        "with_openmp": False,
        "with_pcre": False,
        "with_valgrind": False,
    }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        copy(self, "gkbuild.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.enable_gkregex

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("gklib/5.1.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        rm(self, "*.pdf", self.source_folder, recursive=True)
        copy(self, "CMakeLists.txt", self.export_sources_folder, self.source_folder)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["VALGRIND"] = self.options.with_valgrind
        tc.variables["OPENMP"] = self.options.with_openmp
        tc.variables["PCRE"] = self.options.with_pcre
        tc.variables["GKREGEX"] = self.settings.os == "Windows" or self.options.enable_gkregex
        tc.variables["GKRAND"] = self.options.enable_gkrand
        if self.settings.build_type == "Debug":
            tc.preprocessor_definitions["DEBUG"] = ""
        else:
            # NDEBUG is defined by default by CMake
            # tc.preprocessor_definitions["NDEBUG"] = ""
            tc.preprocessor_definitions["NDEBUG2"] = ""
        bits = 64 if self.options.with_64bit_types else 32
        tc.preprocessor_definitions["IDXTYPEWIDTH"] = str(bits)
        tc.preprocessor_definitions["REALTYPEWIDTH"] = str(bits)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.cmake", self.package_folder, recursive=True)
        rm(self, "*.pc", self.package_folder, recursive=True)
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["metis"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.defines.append("LINUX")
        elif self.settings.os == "Windows":
            self.cpp_info.defines.append("WIN32")
            self.cpp_info.defines.append("MSC")
            self.cpp_info.defines.append("_CRT_SECURE_NO_DEPRECATE")
        elif self.settings.os == "Macos":
            self.cpp_info.defines.append("MACOS")
        elif self.settings.os == "SunOS":
            self.cpp_info.defines.append("SUNOS")

        if is_msvc(self):
            self.cpp_info.defines.append("__thread=__declspec(thread)")

        bits = 64 if self.options.with_64bit_types else 32
        self.cpp_info.defines.append(f"IDXTYPEWIDTH={bits}")
        self.cpp_info.defines.append(f"REALTYPEWIDTH={bits}")

        # Defines for GKLib headers
        if self.settings.os == "Windows" or self.options.enable_gkregex:
            self.cpp_info.defines.append("USE_GKREGEX")
        if self.options.enable_gkrand:
            self.cpp_info.defines.append("USE_GKRAND")
        if self.options.with_pcre:
            self.cpp_info.defines.append("__WITHPCRE__")
        if self.options.with_openmp:
            self.cpp_info.defines.append("__OPENMP__")
