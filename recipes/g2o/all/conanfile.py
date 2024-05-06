import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm, rmdir, save, export_conandata_patches, apply_conandata_patches, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class G2oConan(ConanFile):
    name = "g2o"
    description = "g2o: A General Framework for Graph Optimization"
    license = "BSD-2-Clause", "GPL-3.0-or-later", "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/RainerKuemmerle/g2o"
    topics = ("graph-optimization", "slam", "state-estimation", "computer-vision", "robotics")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_slam2d_types": [True, False],
        "build_slam2d_addon_types": [True, False],
        "build_data_types": [True, False],
        "build_sclam2d_types": [True, False],
        "build_slam3d_types": [True, False],
        "build_slam3d_addon_types": [True, False],
        "build_sba_types": [True, False],
        "build_icp_types": [True, False],
        "build_sim3_types": [True, False],
        "fast_math": [True, False],
        "no_implicit_ownership_of_objects": [True, False],
        "sse_autodetect": [True, False],
        "sse2": [True, False],
        "sse3": [True, False],
        "sse4_1": [True, False],
        "sse4_2": [True, False],
        "sse4_a": [True, False],
        "with_openmp": [True, False],
        "with_cholmod": [True, False],
        "with_csparse": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_slam2d_types": True,
        "build_slam2d_addon_types": True,
        "build_data_types": True,
        "build_sclam2d_types": True,
        "build_slam3d_types": True,
        "build_slam3d_addon_types": True,
        "build_sba_types": True,
        "build_icp_types": True,
        "build_sim3_types": True,
        "fast_math": False,
        "no_implicit_ownership_of_objects": False,
        "sse_autodetect": False,
        # All SSE extensions except for SSE4a (34%) have a 99%+ adoption rate
        # as of 2024-01 in https://store.steampowered.com/hwsurvey
        "sse2": True,
        "sse3": True,
        "sse4_1": True,
        "sse4_2": True,
        "sse4_a": False,
        "with_openmp": False,
        "with_cholmod": False,
        "with_csparse": False,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12",
        }

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "FindSuiteSparse.cmake", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.sse_autodetect:
            del self.info.options.sse2
            del self.info.options.sse3
            del self.info.options.sse4_1
            del self.info.options.sse4_2
            del self.info.options.sse4_a
        if not self.info.options.build_slam2d_types:
            del self.info.options.build_slam2d_addon_types
            del self.info.options.build_sclam2d_types
            del self.info.options.build_data_types
        if not self.info.options.build_slam3d_types:
            del self.info.options.build_slam3d_addon_types
            del self.info.options.build_sba_types
            del self.info.options.build_icp_types
            del self.info.options.build_sim3_types

    def requirements(self):
        # Used in public core/eigen_types.h
        self.requires("eigen/3.4.0", transitive_headers=True, transitive_libs=True)
        # Used in stuff/logger.h
        self.requires("spdlog/1.13.0", transitive_headers=True, transitive_libs=True)
        # Used in stuff/opengl_wrapper.h
        self.requires("opengl/system", transitive_headers=True, transitive_libs=True)
        self.requires("freeglut/3.4.0", transitive_headers=True, transitive_libs=True)
        if self.options.with_openmp and self.settings.compiler in ["clang", "apple-clang"]:
            # Used in core/openmp_mutex.h, also '#pragma omp' is used in several core public headers
            self.requires("llvm-openmp/17.0.6", transitive_headers=True, transitive_libs=True)
        if self.options.with_cholmod:
            self.requires("suitesparse-cholmod/5.2.1")
        if self.options.with_csparse:
            self.requires("suitesparse-cxsparse/4.4.0")

        # TODO: optional dependencies
        # self.requires("qt/5.15.12")
        # self.requires("libqglviewer/x.y.z")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.os == "Windows" and self.options.shared:
            # Build fails with "unresolved external symbol "public: __cdecl g2o::internal::LoggerInterface::LoggerInterface(void)"
            raise ConanInvalidConfiguration("g2o does not currently support shared libraries on Windows")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["G2O_BUILD_EXAMPLES"] = False
        tc.variables["G2O_BUILD_APPS"] = False
        tc.variables["G2O_USE_OPENMP"] = self.options.with_openmp
        tc.variables["G2O_USE_CHOLMOD"] = self.options.with_cholmod
        tc.variables["G2O_USE_CSPARSE"] = self.options.with_csparse
        tc.variables["G2O_USE_OPENGL"] = True
        tc.variables["G2O_USE_LOGGING"] = True
        tc.variables["G2O_BUILD_SLAM2D_TYPES"] = self.options.build_slam2d_types
        tc.variables["G2O_BUILD_SLAM2D_ADDON_TYPES"] = self.options.build_slam2d_addon_types
        tc.variables["G2O_BUILD_DATA_TYPES"] = self.options.build_data_types
        tc.variables["G2O_BUILD_SCLAM2D_TYPES"] = self.options.build_sclam2d_types
        tc.variables["G2O_BUILD_SLAM3D_TYPES"] = self.options.build_slam3d_types
        tc.variables["G2O_BUILD_SLAM3D_ADDON_TYPES"] = self.options.build_slam3d_addon_types
        tc.variables["G2O_BUILD_SBA_TYPES"] = self.options.build_sba_types
        tc.variables["G2O_BUILD_ICP_TYPES"] = self.options.build_icp_types
        tc.variables["G2O_BUILD_SIM3_TYPES"] = self.options.build_sim3_types
        tc.variables["G2O_FAST_MATH"] = self.options.fast_math
        tc.variables["G2O_NO_IMPLICIT_OWNERSHIP_OF_OBJECTS"] = self.options.no_implicit_ownership_of_objects
        tc.variables["DO_SSE_AUTODETECT"] = self.options.sse_autodetect
        tc.variables["DISABLE_SSE2"] = not self.options.sse2
        tc.variables["DISABLE_SSE3"] = not self.options.sse3
        tc.variables["DISABLE_SSE4_1"] = not self.options.sse4_1
        tc.variables["DISABLE_SSE4_2"] = not self.options.sse4_2
        tc.variables["DISABLE_SSE4_A"] = not self.options.sse4_a

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("freeglut", "cmake_target_name", "FreeGLUT::freeglut")
        # CXSparse is a compatible extension of CSparse
        deps.set_property("suitesparse-cxsparse", "cmake_file_name", "CSPARSE")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        copy(self, "FindSuiteSparse.cmake", self.export_sources_folder, os.path.join(self.source_folder, "cmake_modules"))
        save(self, os.path.join(self.source_folder, "g2o", "EXTERNAL", "CMakeLists.txt"), "")
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "find_package(CSparse)", "find_package(CSPARSE)")
        replace_in_file(self, os.path.join(self.source_folder, "g2o", "solvers", "csparse", "CMakeLists.txt"),
                        "$<BUILD_INTERFACE:${CSPARSE_INCLUDE_DIR}>",
                        '"$<BUILD_INTERFACE:${CSPARSE_INCLUDE_DIR}>"')

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "license-*.txt", os.path.join(self.source_folder, "doc"), os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        #  https://github.com/RainerKuemmerle/g2o/blob/20230806_git/cmake_modules/FindG2O.cmake
        self.cpp_info.set_property("cmake_module_file_name", "G2O")
        # https://github.com/RainerKuemmerle/g2o/blob/20230806_git/CMakeLists.txt#L495
        self.cpp_info.set_property("cmake_file_name", "g2o")

        def _add_component(name, requires=None):
            self.cpp_info.components[name].set_property("cmake_target_name", f"g2o::{name}")
            self.cpp_info.components[name].libs = [f"g2o_{name}"]
            self.cpp_info.components[name].requires = requires or []

        # Core libraries
        self.cpp_info.components["g2o_ceres_ad"].set_property("cmake_target_name", "g2o::g2o_ceres_ad")
        _add_component("stuff", requires=["spdlog::spdlog", "eigen::eigen"])
        _add_component("core", requires=["stuff", "eigen::eigen", "g2o_ceres_ad"])
        _add_component("opengl_helper", requires=["opengl::opengl", "freeglut::freeglut", "eigen::eigen"])

        # Solvers
        _add_component("solver_dense", requires=["core"])
        _add_component("solver_eigen", requires=["core"])
        _add_component("solver_pcg", requires=["core"])
        _add_component("solver_structure_only", requires=["core"])
        if self.options.build_slam2d_types:
            _add_component("solver_slam2d_linear", requires=["core", "solver_eigen", "types_slam2d"])
        if self.options.with_cholmod:
            _add_component("solver_cholmod", requires=["core", "suitesparse-cholmod::suitesparse-cholmod"])
        if self.options.with_csparse:
            _add_component("csparse_extension", requires=["stuff", "suitesparse-cxsparse::suitesparse-cxsparse", "eigen::eigen"])
            _add_component("solver_csparse", requires=["core", "csparse_extension"])

        # Types
        if self.options.build_slam2d_types:
            _add_component("types_slam2d", requires=["core", "opengl_helper"])
            if self.options.build_slam2d_addon_types:
                _add_component("types_slam2d_addons", requires=["core", "types_slam2d", "opengl_helper"])
            if self.options.build_sclam2d_types:
                _add_component("types_sclam2d", requires=["core", "opengl_helper", "types_slam2d"])
            if self.options.build_data_types:
                _add_component("types_data", requires=["core", "types_slam2d", "opengl_helper"])
        if self.options.build_slam3d_types:
            _add_component("types_slam3d", requires=["core", "opengl_helper"])
            if self.options.build_slam3d_addon_types:
                _add_component("types_slam3d_addons", requires=["core", "types_slam3d", "opengl_helper"])
            if self.options.build_sba_types:
                _add_component("types_sba", requires=["core", "types_slam3d"])
                if self.options.build_icp_types:
                    _add_component("types_icp", requires=["core", "types_sba", "types_slam3d"])
                if self.options.build_sim3_types:
                    _add_component("types_sim3", requires=["core", "types_sba"])

        if self.options.with_openmp:
            openmp_flags = []
            if self.settings.compiler in ["clang", "apple-clang"]:
                self.cpp_info.components["core"].requires.append("llvm-openmp::llvm-openmp")
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]
            elif self.settings.compiler == "gcc":
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler == "intel-cc":
                openmp_flags = ["/Qopenmp"] if self.settings.os == "Windows" else ["-Qopenmp"]
            elif is_msvc(self):
                openmp_flags = ["-openmp"]
            # '#pragma omp parallel for' is used in multiple public headers in core
            self.cpp_info.components["core"].cxxflags = openmp_flags
            self.cpp_info.components["core"].sharedlinkflags = openmp_flags
            self.cpp_info.components["core"].exelinkflags = openmp_flags

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["stuff"].system_libs.append("m")
            self.cpp_info.components["stuff"].system_libs.append("rt")
