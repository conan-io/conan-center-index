from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, rm, rmdir, mkdir, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import glob
import os

required_conan_version = ">=1.53.0"


class OpenmvgConan(ConanFile):
    name = "openmvg"
    description = (
        "OpenMVG provides an end-to-end 3D reconstruction from images framework "
        "compounded of libraries, binaries, and pipelines."
    )
    license = "MPL-2.0"
    topics = ("computer-vision", "geometry", "structure-from-motion", "sfm",
              "multi-view-geometry", "photogrammetry", "3d-reconstruction")
    homepage = "https://github.com/openMVG/openMVG"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_ligt": [True, False],
        "programs": [True, False],
        "with_avx": [False, "avx", "avx2"],
        "with_jpeg": ["libjpeg", "libjpeg-turbo", "mozjpeg"],
        "with_openmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_ligt": False, # patent-protected and CC-BY-SA-licensed
        "programs": True,
        "with_avx": False,
        "with_jpeg": "libjpeg",
        "with_openmp": False, # TODO: can be enabled after #22353
    }

    short_paths = True

    def export_sources(self):
        export_conandata_patches(self)
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src", "src"))
        copy(self, "OptimizeForArchitecture.cmake", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ["x86", "x86_64"]:
            del self.options.with_avx

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("cereal/1.3.2", transitive_headers=True)
        if Version(self.version) >= "2.1":
            self.requires("ceres-solver/2.2.0")
        else:
            self.requires("ceres-solver/2.1.0")
        self.requires("coin-clp/1.17.7")
        self.requires("coin-lemon/1.3.1", transitive_headers=True, transitive_libs=True)
        self.requires("coin-osi/0.108.7")
        self.requires("coin-utils/2.11.9")
        self.requires("eigen/3.4.0", transitive_headers=True)
        self.requires("flann/1.9.2", transitive_headers=True, transitive_libs=True)
        if self.options.with_jpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_jpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/3.0.2")
        elif self.options.with_jpeg == "mozjpeg":
            self.requires("mozjpeg/4.1.5")
        self.requires("libpng/[>=1.6 <2]")
        self.requires("libtiff/4.6.0")
        if self.options.with_openmp:
            # '#pragma omp' is used in public headers
            self.requires("llvm-openmp/17.0.6", transitive_headers=True, transitive_libs=True)
        # TODO: unvendor vlfeat

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration(
                f"{self.ref} can' be built by gcc < 7 due to usage of some ceres-solver templated code "
                "which hits a bug in gcc < 7: https://gcc.gnu.org/bugzilla/show_bug.cgi?id=56480"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_PROJECT_openMVG_INCLUDE"] = "conan_deps.cmake"
        tc.variables["OpenMVG_BUILD_SHARED"] = self.options.shared
        tc.variables["OpenMVG_BUILD_TESTS"] = False
        tc.variables["OpenMVG_BUILD_DOC"] = False
        tc.variables["OpenMVG_BUILD_EXAMPLES"] = False
        tc.variables["OpenMVG_BUILD_OPENGL_EXAMPLES"] = False
        tc.variables["OpenMVG_BUILD_SOFTWARES"] = self.options.programs
        tc.variables["OpenMVG_BUILD_GUI_SOFTWARES"] = False
        tc.variables["OpenMVG_BUILD_COVERAGE"] = False
        tc.variables["OpenMVG_USE_LIGT"] = self.options.enable_ligt
        tc.variables["OpenMVG_USE_OPENMP"] = self.options.with_openmp
        tc.variables["OpenMVG_USE_OPENCV"] = False
        tc.variables["OpenMVG_USE_OCVSIFT"] = False
        # OpenMVG expects these CMake variables to be set automatically by a custom OptimizeForArchitecture macro
        # but this macro is fragile and broken in case of cross-build. Moreover it may lead to non-portable binaries.
        # Therefore macro is disabled through patch and we allow users to decide whether they want specific avx
        # optimization.
        tc.variables["USE_SSE2"] = self.settings.arch in ["x86", "x86_64"]
        tc.variables["USE_AVX"] = self.options.get_safe("with_avx") in ["avx", "avx2"]
        tc.variables["USE_AVX2"] = self.options.get_safe("with_avx") == "avx2"
        # Even though openmvg requires C++11, recent versions of cereal require C++14
        # and targets generated by CMakeDeps don't propagate compile features (yet?)
        # see https://github.com/conan-io/conan/issues/10281
        if Version(self.dependencies["ceres-solver"].ref.version) >= "2.0.0" and not valid_min_cppstd(self, "14"):
            tc.variables["CMAKE_CXX_STANDARD"] = "14"

        if self.settings.os == "Linux":
            # Workaround for: https://github.com/conan-io/conan/issues/13560
            libdirs_host = [l for dependency in self.dependencies.host.values() for l in dependency.cpp_info.aggregated_components().libdirs]
            tc.variables["CMAKE_BUILD_RPATH"] = ";".join(libdirs_host)

        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"

        if self.settings.os == "Windows":
            # Fix a missing /bigobj flag for 'matching' and 'multiview' components
            # and add the equivalent for MinGW as well
            if is_msvc(self):
                tc.extra_cflags.append("/bigobj")
                tc.extra_cxxflags.append("/bigobj")
            elif self.settings.compiler == "gcc":
                tc.extra_cflags.append("-Wa,-mbig-obj")
                tc.extra_cxxflags.append("-Wa,-mbig-obj")

        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("cereal", "cmake_file_name", "cereal")
        deps.set_property("ceres-solver", "cmake_file_name", "Ceres")
        deps.set_property("coin-clp", "cmake_file_name", "Clp")
        deps.set_property("coin-lemon", "cmake_file_name", "Lemon")
        deps.set_property("coin-osi", "cmake_file_name", "Osi")
        deps.set_property("coin-utils", "cmake_file_name", "CoinUtils")
        deps.set_property("flann", "cmake_file_name", "Flann")
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Override OpenMVG's OptimizeForArchitecture.cmake
        copy(self, "OptimizeForArchitecture.cmake", self.export_sources_folder, os.path.join(self.source_folder, "src", "cmakeFindModules"))
        # bypass a check for submodules
        mkdir(self, os.path.join(self.source_folder, "src", "dependencies", "cereal", "include"))
        # ensure internal dependencies are not used by accident
        cmakelists = os.path.join(self.source_folder, "src", "CMakeLists.txt")
        replace_in_file(self, cmakelists, "set(OpenMVG_USE_INTERNAL_", "# set(OpenMVG_USE_INTERNAL_")
        replace_in_file(self, cmakelists, "find_package(OpenMP)", "find_package(OpenMP REQUIRED)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "src"))
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # remove empty third-party include dirs
        rmdir(self, os.path.join(self.package_folder, "include", "openMVG_dependencies", "cereal"))
        rmdir(self, os.path.join(self.package_folder, "include", "openMVG_dependencies", "glfw"))
        rmdir(self, os.path.join(self.package_folder, "include", "openMVG_dependencies", "osi_clp"))
        for dll_file in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
            rename(self, src=dll_file, dst=os.path.join(self.package_folder, "bin", os.path.basename(dll_file)))
        rm(self, "*.cmake", os.path.join(self.package_folder, "lib"))
        if Version(self.version) >= "2.1":
            share_dir = os.path.join(self.package_folder, "lib", "openMVG")
        else:
            share_dir = os.path.join(self.package_folder, "share", "openMVG")
        rmdir(self, os.path.join(share_dir, "cmake"))
        mkdir(self, os.path.join(self.package_folder, "res"))
        rename(self, share_dir, os.path.join(self.package_folder, "res", "openMVG"))

    @property
    def _openmp_flags(self):
        if self.settings.compiler == "clang":
            return ["-fopenmp=libomp"]
        elif self.settings.compiler == "apple-clang":
            return ["-Xclang", "-fopenmp"]
        elif self.settings.compiler == "gcc":
            return ["-fopenmp"]
        elif self.settings.compiler == "intel-cc":
            return ["-Qopenmp"]
        elif self.settings.compiler == "sun-cc":
            return ["-xopenmp"]
        elif is_msvc(self):
            return ["-openmp"]
        return None

    @property
    def _openmvg_components(self):
        def jpeg():
            if self.options.with_jpeg == "libjpeg":
                return ["libjpeg::libjpeg"]
            elif self.options.with_jpeg == "libjpeg-turbo":
                return ["libjpeg-turbo::jpeg"]
            elif self.options.with_jpeg == "mozjpeg":
                return ["mozjpeg::libjpeg"]

        def pthread():
            if self.settings.os in ["Linux", "FreeBSD"]:
                return ["pthread"]
            return []

        return {
            "openmvg_camera": {
                "target": "openMVG_camera",
                "requires": ["openmvg_numeric", "cereal::cereal"],
            },
            "openmvg_exif": {
                "target": "openMVG_exif",
                "libs": ["openMVG_exif"],
                "requires": ["openmvg_easyexif"],
            },
            "openmvg_features": {
                "target": "openMVG_features",
                "libs": ["openMVG_features"],
                "requires": ["openmvg_fast", "openmvg_stlplus", "eigen::eigen", "cereal::cereal"],
            },
            "openmvg_geodesy": {
                "target": "openMVG_geodesy",
                "requires": ["openmvg_numeric"],
            },
            "openmvg_geometry": {
                "target": "openMVG_geometry",
                "libs": ["openMVG_geometry"],
                "requires": ["openmvg_numeric", "openmvg_linearprogramming", "cereal::cereal"],
            },
            "openmvg_graph": {
                "target": "openMVG_graph",
                "requires": ["coin-lemon::coin-lemon"],
            },
            "openmvg_image": {
                "target": "openMVG_image",
                "libs": ["openMVG_image"],
                "requires": ["openmvg_numeric", "libpng::libpng", "libtiff::libtiff"] + jpeg(),
            },
            "openmvg_linearprogramming": {
                "target": "openMVG_linearProgramming",
                "libs": ["openMVG_linearProgramming"],
                "requires": ["openmvg_numeric", "coin-clp::coin-clp", "coin-osi::coin-osi", "coin-utils::coin-utils"],
            },
            "openmvg_linftycomputervision": {
                "target": "openMVG_lInftyComputerVision",
                "libs": ["openMVG_lInftyComputerVision"],
                "requires": ["openmvg_linearprogramming", "openmvg_multiview"],
            },
            "openmvg_matching": {
                "target": "openMVG_matching",
                "libs": ["openMVG_matching"],
                "requires": ["openmvg_features", "openmvg_stlplus", "cereal::cereal", "flann::flann"],
                "system_libs": pthread(),
            },
            "openmvg_kvld": {
                "target": "openMVG_kvld",
                "libs": ["openMVG_kvld"],
                "requires": ["openmvg_features", "openmvg_image"],
            },
            "openmvg_matching_image_collection": {
                "target": "openMVG_matching_image_collection",
                "libs": ["openMVG_matching_image_collection"],
                "requires": ["openmvg_matching", "openmvg_multiview"],
            },
            "openmvg_multiview": {
                "target": "openMVG_multiview",
                "libs": ["openMVG_multiview"],
                "requires": ["openmvg_numeric", "openmvg_graph", "ceres-solver::ceres-solver"],
            },
            "openmvg_numeric": {
                "target": "openMVG_numeric",
                "libs": ["openMVG_numeric"],
                "requires": ["eigen::eigen"],
                "defines": [(is_msvc(self), ["_USE_MATH_DEFINES"])],
            },
            "openmvg_robust_estimation": {
                "target": "openMVG_robust_estimation",
                "libs": ["openMVG_robust_estimation"],
                "requires": ["openmvg_numeric"],
            },
            "openmvg_sfm": {
                "target": "openMVG_sfm",
                "libs": ["openMVG_sfm"],
                "requires": [
                    "openmvg_geometry", "openmvg_features", "openmvg_graph", "openmvg_matching",
                    "openmvg_multiview", "openmvg_image", "openmvg_linftycomputervision",
                    "openmvg_system", "openmvg_stlplus", "cereal::cereal", "ceres-solver::ceres-solver",
                ],
            },
            "openmvg_system": {
                "target": "openMVG_system",
                "libs": ["openMVG_system"],
                "requires": ["openmvg_numeric"],
            },
            # vendored libs
            "openmvg_easyexif": {
                "target": "openMVG_easyexif",
                "libs": ["openMVG_easyexif"],
            },
            "openmvg_fast": {
                "target": "openMVG_fast",
                "libs": ["openMVG_fast"],
            },
            "openmvg_stlplus": {
                "target": "openMVG_stlplus",
                "libs": ["openMVG_stlplus"],
            },
            "openmvg_svg": {
                "target": "openMVG_svg",
            },
            "openmvg_vlsift": {
                "target": "vlsift",
                "libs": ["vlsift"],
            },
        }

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenMVG")

        for component, values in self._openmvg_components.items():
            target = values["target"]
            libs = values.get("libs", [])
            defines = []
            for _condition, _defines in values.get("defines", []):
                if _condition:
                    defines.extend(_defines)

            self.cpp_info.components[component].set_property("cmake_target_name", f"OpenMVG::{target}")
            if libs:
                self.cpp_info.components[component].libs = libs
            self.cpp_info.components[component].defines = defines
            self.cpp_info.components[component].requires = values.get("requires", [])
            self.cpp_info.components[component].system_libs = values.get("system_libs", [])
            self.cpp_info.components[component].resdirs = ["res"]

            # TODO: to remove in conan v2
            self.cpp_info.components[component].names["cmake_find_package"] = target
            self.cpp_info.components[component].names["cmake_find_package_multi"] = target

        if self.options.with_openmp:
            for component_name in ["cameras", "features", "image", "matching", "matching_image_collection", "robust_estimation", "sfm", "vlsift"]:
                component = self.cpp_info.components[f"openmvg_{component_name}"]
                component.requires.append("llvm-openmp::llvm-openmp")
                component.cflags += self._openmp_flags
                component.cxxflags += self._openmp_flags

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "OpenMVG"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenMVG"
        if self.options.programs:
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
