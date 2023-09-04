from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rmdir, save
from conan.tools.microsoft import check_min_vs, is_msvc, msvc_runtime_flag
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


class GtsamConan(ConanFile):
    name = "gtsam"
    license = "BSD-3-Clause"
    homepage = "https://github.com/borglab/gtsam"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("GTSAM is a library of C++ classes that implement "
                   "smoothing and mapping (SAM) in robotics and vision")
    topics = ("mapping", "smoothing", "optimization", "factor-graphs")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "allow_deprecated": [True, False],
        "allow_deprecated_since_V4": [True, False, "deprecated"],
        "build_type_postfixes": [True, False],
        "build_unstable": [True, False],
        "build_with_march_native": [True, False],
        "default_allocator": [None, "STL", "BoostPool", "TBB", "tcmalloc"],
        "disable_new_timers": [True, False],
        "enable_consistency_checks": [True, False],
        "install_cppunitlite": [True, False],
        "install_matlab_toolbox": [True, False],
        "pose3_expmap": [True, False],
        "rot3_expmap": [True, False],
        "slow_but_correct_betweenfactor": [True, False],
        "support_nested_dissection": [True, False],
        "tangent_preintegration": [True, False],
        "throw_cheirality_exception": [True, False],
        "use_quaternions": [True, False],
        "with_TBB": [True, False],
        "with_eigen_MKL": [True, False],
        "with_eigen_MKL_OPENMP": [True, False],

        # Removed since v4.1
        "build_wrap": [True, False],
        "install_cython_toolbox": [True, False],
        "typedef_points_to_vectors": [True, False],
        "wrap_serialization": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "allow_deprecated": True,
        "allow_deprecated_since_V4": "deprecated",
        "build_type_postfixes": True,
        "build_unstable": True,
        "build_with_march_native": False,
        "default_allocator": None,
        "disable_new_timers": False,
        "enable_consistency_checks": False,
        "install_cppunitlite": True,
        "install_matlab_toolbox": False,
        "pose3_expmap": False,
        "rot3_expmap": False,
        "slow_but_correct_betweenfactor": False,
        "support_nested_dissection": False,
        "tangent_preintegration": False,
        "throw_cheirality_exception": True,
        "use_quaternions": False,
        "with_TBB": False,
        "with_eigen_MKL": False,
        "with_eigen_MKL_OPENMP": False,

        # < v4.1 only
        "build_wrap": False,
        "install_cython_toolbox": False,
        "typedef_points_to_vectors": False,
        "wrap_serialization": True,
    }
    options_description = {
        "allow_deprecated": "Allow use of deprecated methods/functions",
        "build_type_postfixes": "Append the build type to the name of compiled libraries",
        "build_unstable": "Enable building of gtsam_unstable",
        "build_with_march_native": "Build with all instructions supported by native architecture (binary may not be portable!)",
        "default_allocator": "Set preferred memory allocator. If unset, defaults to STL or to TBB, if with_TBB is enabled",
        "disable_new_timers": "Disables using Boost.chrono for timing",
        "enable_consistency_checks": "Enable expensive consistency checks",
        "install_cppunitlite": "Install CppUnitLite library as a component",
        "install_matlab_toolbox": "Install MATLAB toolbox",
        "pose3_expmap": "Use Pose3::EXPMAP as the default mode. If disabled, Pose3::FIRST_ORDER will be used.",
        "rot3_expmap": ("Ignore if GTSAM_USE_QUATERNIONS is OFF (Rot3::EXPMAP by default). "
                        "Otherwise, enable Rot3::EXPMAP, or if disabled, use Rot3::CAYLEY."),
        "slow_but_correct_betweenfactor": "Use the slower but correct version of BetweenFactor",
        "support_nested_dissection": "Support Metis-based nested dissection",
        "tangent_preintegration": "Use the new ImuFactor with integration on tangent space",
        "throw_cheirality_exception": "Throw exception when a triangulated point is behind a camera",
        "use_quaternions": ("Enable an internal Quaternion representation for rotations instead of rotation matrices. "
                            "If enabled, Rot3::EXPMAP is enforced by default."),
        "with_TBB": "Use Intel Threaded Building Blocks (TBB)",
        "with_eigen_MKL": "Eigen will use Intel MKL if available",
        "with_eigen_MKL_OPENMP": "Eigen, when using Intel MKL, will also use OpenMP for multithreading if available",

        # < v4.1 only
        "build_wrap": "Build Matlab/Cython wrap utility (necessary for Matlab/Cython interface)",
        "install_cython_toolbox": "Install Cython toolbox",
        "typedef_points_to_vectors": "Typedef Point2 and Point3 to Eigen::Vector equivalents",
        "wrap_serialization": "Allow wrapped objects to be saved via boost.serialization",
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) >= "4.1":
            del self.options.build_wrap
            del self.options.install_cython_toolbox
            del self.options.typedef_points_to_vectors
            del self.options.wrap_serialization
        else:
            del self.options.slow_but_correct_betweenfactor

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.with_TBB:
            self.options["onetbb"].tbbmalloc = True
        if self.options.allow_deprecated_since_V4 != "deprecated":
            self.output.warn("'allow_deprecated_since_V4' option is deprecated. Use 'allow_deprecated' instead.")


    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.83.0", transitive_headers=True)
        self.requires("eigen/3.4.0", transitive_headers=True)
        if self.options.with_TBB:
            self.requires("onetbb/2021.10.0", transitive_headers=True)
        if self.options.default_allocator == "tcmalloc":
            self.requires("gperftools/2.11.0")
        # TODO: add use_vendored_metis=False option
        # if self.options.support_nested_dissection and not self.options.use_vendored_metis:
        #     # Used in a public header here:
        #     # https://github.com/borglab/gtsam/blob/4.2a9/gtsam_unstable/partition/FindSeparator-inl.h#L23-L27
        #     self.requires("metis/5.1.1", transitive_headers=True)

    @property
    def _required_boost_components(self):
        # Based on https://github.com/borglab/gtsam/blob/4.2a9/cmake/HandleBoost.cmake#L26
        return [
            "chrono",
            "date_time",
            "filesystem",
            "program_options",
            "regex",
            "serialization",
            "system",
            "thread",
            "timer",
        ]

    def validate(self):
        miss_boost_required_comp = any(
            self.dependencies["boost"].options.get_safe(f"without_{boost_comp}", True)
            for boost_comp in self._required_boost_components
        )
        if self.dependencies["boost"].options.header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires non header-only boost with these components: "
                f"{', '.join(self._required_boost_components)}"
            )

        if self.options.with_TBB:
            if self.options.default_allocator in [None, "TBB"]:
                if not self.dependencies["onetbb"].options.tbbmalloc:
                    raise ConanInvalidConfiguration("GTSAM with TBB requires onetbb/*:tbbmalloc=True")
            elif self.options.default_allocator != "tcmalloc":
                raise ConanInvalidConfiguration(
                    "with_TBB option cannot be used with"
                    f" default_allocator={self.options.default_allocator}"
                )
        elif self.options.default_allocator == "TBB":
            raise ConanInvalidConfiguration("default_allocator=TBB requires with_TBB=True")

        check_min_vs(self, "191")

        if Version(self.version) >= "4.1" and is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support shared builds with MSVC. See"
                "https://github.com/borglab/gtsam/issues/1087"
                if Version(self.version) < "4.2"
                else "https://github.com/borglab/gtsam/issues/1541"
            )

        if self.options.allow_deprecated_since_V4 != "deprecated":
            self.output.warn(
                "'allow_deprecated_since_V4' option is deprecated. Use 'allow_deprecated' instead."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        # https://github.com/borglab/gtsam/blob/4.2a9/cmake/HandleGeneralOptions.cmake
        tc.variables["GTSAM_BUILD_UNSTABLE"] = self.options.build_unstable
        tc.variables["GTSAM_UNSTABLE_BUILD_PYTHON"] = False
        tc.variables["GTSAM_UNSTABLE_INSTALL_MATLAB_TOOLBOX"] = self.options.install_matlab_toolbox
        tc.variables["GTSAM_USE_QUATERNIONS"] = self.options.use_quaternions
        tc.variables["GTSAM_POSE3_EXPMAP"] = self.options.pose3_expmap
        tc.variables["GTSAM_ROT3_EXPMAP"] = self.options.rot3_expmap
        tc.variables["GTSAM_ENABLE_CONSISTENCY_CHECKS"] = self.options.enable_consistency_checks
        tc.variables["GTSAM_WITH_TBB"] = self.options.with_TBB
        tc.variables["GTSAM_WITH_EIGEN_MKL"] = self.options.with_eigen_MKL
        tc.variables["GTSAM_WITH_EIGEN_MKL_OPENMP"] = self.options.with_eigen_MKL_OPENMP
        tc.variables["GTSAM_THROW_CHEIRALITY_EXCEPTION"] = self.options.throw_cheirality_exception
        tc.variables["GTSAM_BUILD_PYTHON"] = False
        tc.variables["GTSAM_INSTALL_MATLAB_TOOLBOX"] = self.options.install_matlab_toolbox
        tc.variables["GTSAM_ALLOW_DEPRECATED_SINCE_V4"] = self.options.allow_deprecated
        if self.options.allow_deprecated_since_V4 != "deprecated":
            tc.variables["GTSAM_ALLOW_DEPRECATED_SINCE_V4"] = self.options.allow_deprecated_since_V4
        tc.variables["GTSAM_ALLOW_DEPRECATED_SINCE_V41"] = self.options.allow_deprecated
        tc.variables["GTSAM_ALLOW_DEPRECATED_SINCE_V42"] = self.options.allow_deprecated
        tc.variables["GTSAM_SUPPORT_NESTED_DISSECTION"] = self.options.support_nested_dissection
        tc.variables["GTSAM_TANGENT_PREINTEGRATION"] = self.options.tangent_preintegration
        # Added in 4.1+
        if Version(self.version) >= "4.1":
            tc.variables["GTSAM_SLOW_BUT_CORRECT_BETWEENFACTOR"] = self.options.slow_but_correct_betweenfactor
        tc.variables["GTSAM_BUILD_WITH_CCACHE"] = False
        # https://github.com/borglab/gtsam/blob/4.2a9/cmake/HandleAllocators.cmake
        if self.options.default_allocator is not None:
            tc.variables["GTSAM_DEFAULT_ALLOCATOR"] = self.options.default_allocator
        # https://github.com/borglab/gtsam/blob/4.2a9/cmake/GtsamBuildTypes.cmake#L59
        tc.variables["GTSAM_BUILD_TYPE_POSTFIXES"] = self.options.build_type_postfixes
        # https://github.com/borglab/gtsam/blob/4.2a9/cmake/GtsamBuildTypes.cmake#L193
        tc.variables["GTSAM_BUILD_WITH_MARCH_NATIVE"] = self.options.build_with_march_native
        # https://github.com/borglab/gtsam/blob/4.2a9/cmake/HandleBoost.cmake#L36
        tc.variables["GTSAM_DISABLE_NEW_TIMERS"] = self.options.disable_new_timers
        # https://github.com/borglab/gtsam/blob/4.2a9/CppUnitLite/CMakeLists.txt#L13
        tc.variables["GTSAM_INSTALL_CPPUNITLITE"] = self.options.install_cppunitlite
        # https://github.com/borglab/gtsam/blob/4.2a9/cmake/HandleEigen.cmake#L3
        tc.variables["GTSAM_USE_SYSTEM_EIGEN"] = True
        # https://github.com/borglab/gtsam/blob/4.2a9/cmake/HandleMetis.cmake#L11
        tc.variables["GTSAM_USE_SYSTEM_METIS"] = False
        # https://github.com/borglab/gtsam/blob/4.2a9/gtsam/3rdparty/CMakeLists.txt#L76
        tc.variables["GTSAM_INSTALL_GEOGRAPHICLIB"] = False
        # https://github.com/borglab/gtsam/blob/4.2a9/matlab/CMakeLists.txt#L14-L15
        tc.variables["GTSAM_MEX_BUILD_STATIC_MODULE"] = False
        # https://github.com/borglab/gtsam/blob/4.2a9/cmake/GtsamTesting.cmake#L89-L91
        tc.variables["GTSAM_BUILD_TESTS"] = False
        tc.variables["GTSAM_BUILD_EXAMPLES_ALWAYS"] = False
        tc.variables["GTSAM_BUILD_TIMING_ALWAYS"] = False
        # https://github.com/borglab/gtsam/blob/4.2a9/doc/CMakeLists.txt
        tc.variables["GTSAM_BUILD_DOCS"] = False
        tc.variables["GTSAM_BUILD_DOC_HTML"] = False
        tc.variables["GTSAM_BUILD_DOC_LATEX"] = False

        # Removed in 4.1+
        if Version(self.version) < "4.1":
            # https://github.com/borglab/gtsam/blob/4.0.3/CMakeLists.txt
            tc.variables["GTSAM_BUILD_WRAP"] = self.options.build_wrap
            tc.variables["GTSAM_INSTALL_CYTHON_TOOLBOX"] = self.options.install_cython_toolbox
            tc.variables["GTSAM_TYPEDEF_POINTS_TO_VECTORS"] = self.options.typedef_points_to_vectors
            # https://github.com/borglab/gtsam/blob/4.0.3/wrap/CMakeLists.txt#L15
            tc.variables["GTSAM_WRAP_SERIALIZATION"] = self.options.wrap_serialization

        tc.variables["Boost_USE_STATIC_LIBS"] = not self.dependencies["boost"].options.shared
        tc.variables["Boost_NO_SYSTEM_PATHS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        # Honor vc runtime
        if is_msvc(self):
            gtsam_build_types_cmake = os.path.join(self.source_folder, "cmake", "GtsamBuildTypes.cmake")
            replace_in_file(self, gtsam_build_types_cmake, "/MD ", f"/{msvc_runtime_flag(self)} ")
            replace_in_file(self, gtsam_build_types_cmake, "/MDd ", f"/{msvc_runtime_flag(self)} ")

        if self.options.default_allocator == "tcmalloc":
            handle_allocators_path = os.path.join(self.source_folder, "cmake", "HandleAllocators.cmake")
            if Version(self.version) < "4.1":
                handle_allocators_path = os.path.join(self.source_folder, "CMakeLists.txt")
            replace_in_file(
                self,
                handle_allocators_path,
                "if(GOOGLE",
                "find_package(gperftools REQUIRED)\nset(GOOGLE_PERFTOOLS_FOUND TRUE)\nif(GOOGLE",
            )
            replace_in_file(
                self,
                handle_allocators_path,
                'GTSAM_ADDITIONAL_LIBRARIES "tcmalloc"',
                'GTSAM_ADDITIONAL_LIBRARIES "gperftools::gperftools"',
            )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE.BSD", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "CMake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "gtsam": "GTSAM::gtsam",
                "gtsam_unstable": "GTSAM::gtsam_unstable",
                "metis-gtsam": "GTSAM::metis-gtsam",
                "CppUnitLite": "GTSAM::CppUnitLite",
            }
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "GTSAM")

        gtsam = self.cpp_info.components["libgtsam"]
        gtsam.set_property("cmake_target_name", "gtsam")
        gtsam.libs = ["gtsam"]
        gtsam.requires = [f"boost::{component}" for component in self._required_boost_components]
        gtsam.requires.append("eigen::eigen")
        if self.options.with_TBB:
            gtsam.requires.append("onetbb::onetbb")
        if self.options.default_allocator == "tcmalloc":
            gtsam.requires.append("gperftools::gperftools")
        if self.options.support_nested_dissection:
            gtsam.requires.append("libmetis-gtsam")
        if self.settings.os == "Windows":
            gtsam.system_libs = ["dbghelp"]

        if self.options.build_unstable:
            gtsam_unstable = self.cpp_info.components["libgtsam_unstable"]
            gtsam_unstable.set_property("cmake_target_name", "gtsam_unstable")
            gtsam_unstable.libs = ["gtsam_unstable"]
            gtsam_unstable.requires = ["libgtsam"]

        if self.options.support_nested_dissection:
            metis = self.cpp_info.components["libmetis-gtsam"]
            metis.set_property("cmake_target_name", "metis-gtsam")
            if Version(self.version) >= "4.1":
                metis.libs = ["metis-gtsam"]
            else:
                metis.libs = ["metis"]
            metis.names["pkg_config"] = "metis-gtsam"

        if self.options.install_cppunitlite:
            cppunitlite = self.cpp_info.components["gtsam_CppUnitLite"]
            cppunitlite.set_property("cmake_target_name", "CppUnitLite")
            cppunitlite.libs = ["CppUnitLite"]
            cppunitlite.requires = ["boost::boost"]

        if is_msvc(self) and not self.options.shared:
            for component in self.cpp_info.components.values():
                component.libs = [f"lib{lib}" for lib in component.libs if lib.startswith("gtsam")]
        if self.options.build_type_postfixes and self.settings.build_type != "Release":
            for component in self.cpp_info.components.values():
                component.libs = [f"{lib}{self.settings.build_type}" for lib in component.libs]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "GTSAM"
        self.cpp_info.names["cmake_find_package_multi"] = "GTSAM"
        for component_name, lib_name in [
            ("libgtsam", "gtsam"),
            ("libgtsam_unstable", "gtsam_unstable"),
            ("libmetis-gtsam", "metis-gtsam"),
            ("gtsam_CppUnitLite", "CppUnitLite"),
        ]:
            if component_name in self.cpp_info.components:
                component = self.cpp_info.components[component_name]
                component.names["cmake_find_package"] = lib_name
                component.names["cmake_find_package_multi"] = lib_name
                component.build_modules["cmake_find_package"] = [self._module_file_rel_path]
                component.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
