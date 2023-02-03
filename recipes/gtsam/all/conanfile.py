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
    description = ("GTSAM is a library of C++ classes that implement\
                    smoothing and mapping (SAM) in robotics and vision")
    topics = ("mapping", "smoothing")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_quaternions": [True, False],
        "pose3_expmap": [True, False],
        "rot3_expmap": [True, False],
        "enable_consistency_checks": [True, False],
        "with_TBB": [True, False],
        "with_eigen_MKL": [True, False],
        "with_eigen_MKL_OPENMP": [True, False],
        "throw_cheirality_exception": [True, False],
        "allow_deprecated_since_V4": [True, False],
        "typedef_points_to_vectors": [True, False],
        "support_nested_dissection": [True, False],
        "tangent_preintegration": [True, False],
        "build_wrap": [True, False],
        "wrap_serialization": [True, False],
        "build_unstable": [True, False],
        "disable_new_timers": [True, False],
        "build_type_postfixes": [True, False],
        "install_matlab_toolbox": [True, False],
        "install_cython_toolbox": [True, False],
        "install_cppunitlite": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_quaternions": False,
        "pose3_expmap": False,
        "rot3_expmap": False,
        "enable_consistency_checks": False,
        "with_TBB": False,
        "with_eigen_MKL": False,
        "with_eigen_MKL_OPENMP": False,
        "throw_cheirality_exception": True,
        "allow_deprecated_since_V4": True,
        "typedef_points_to_vectors": False,
        "support_nested_dissection": False,
        "tangent_preintegration": False,
        "build_wrap": False,
        "wrap_serialization": True,
        "build_unstable": True,
        "disable_new_timers": False,
        "build_type_postfixes": True,
        "install_matlab_toolbox": False,
        "install_cython_toolbox": False,
        "install_cppunitlite": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.options.with_TBB:
            self.options["onetbb"].tbbmalloc = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.81.0")
        self.requires("eigen/3.4.0")
        if self.options.with_TBB:
            self.requires("onetbb/2020.3")

    @property
    def _required_boost_components(self):
        return ["serialization", "system", "filesystem", "thread", "date_time", "regex", "timer", "chrono"]

    def validate(self):
        miss_boost_required_comp = any(self.dependencies["boost"].options.get_safe(f"without_{boost_comp}", True)
                                       for boost_comp in self._required_boost_components)
        if self.dependencies["boost"].options.header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires non header-only boost with these components: "
                f"{', '.join(self._required_boost_components)}"
            )

        if self.options.with_TBB and not self.dependencies["onetbb"].options.tbbmalloc:
            raise ConanInvalidConfiguration("gtsam with tbb requires onetbb:tbbmalloc=True")

        check_min_vs(self, "191")

        if Version(self.version) >= "4.1.0" and is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support shared builds with MSVC. See https://github.com/borglab/gtsam/issues/1087"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["GTSAM_USE_QUATERNIONS"] = self.options.use_quaternions
        tc.variables["GTSAM_POSE3_EXPMAP"] = self.options.pose3_expmap
        tc.variables["GTSAM_ROT3_EXPMAP"] = self.options.rot3_expmap
        tc.variables["GTSAM_ENABLE_CONSISTENCY_CHECKS"] = self.options.enable_consistency_checks
        tc.variables["GTSAM_WITH_TBB"] = self.options.with_TBB
        tc.variables["GTSAM_WITH_EIGEN_MKL"] = self.options.with_eigen_MKL
        tc.variables["GTSAM_WITH_EIGEN_MKL_OPENMP"] = self.options.with_eigen_MKL_OPENMP
        tc.variables["GTSAM_THROW_CHEIRALITY_EXCEPTION"] = self.options.throw_cheirality_exception
        tc.variables["GTSAM_ALLOW_DEPRECATED_SINCE_V4"] = self.options.allow_deprecated_since_V4
        tc.variables["GTSAM_TYPEDEF_POINTS_TO_VECTORS"] = self.options.typedef_points_to_vectors
        tc.variables["GTSAM_SUPPORT_NESTED_DISSECTION"] = self.options.support_nested_dissection
        tc.variables["GTSAM_TANGENT_PREINTEGRATION"] = self.options.tangent_preintegration
        tc.variables["GTSAM_BUILD_WITH_CCACHE"] = False
        tc.variables["GTSAM_BUILD_UNSTABLE"] = self.options.build_unstable
        tc.variables["GTSAM_DISABLE_NEW_TIMERS"] = self.options.disable_new_timers
        tc.variables["GTSAM_BUILD_TYPE_POSTFIXES"] = self.options.build_type_postfixes
        tc.variables["GTSAM_BUILD_TESTS"] = False
        tc.variables["Boost_USE_STATIC_LIBS"] = not self.dependencies["boost"].options.shared
        tc.variables["Boost_NO_SYSTEM_PATHS"] = True
        tc.variables["GTSAM_BUILD_DOCS"] = False
        tc.variables["GTSAM_BUILD_DOC_HTML"] = False
        tc.variables["GTSAM_BUILD_EXAMPLES_ALWAYS"] = False
        tc.variables["GTSAM_BUILD_WRAP"] = self.options.build_wrap
        tc.variables["GTSAM_BUILD_WITH_MARCH_NATIVE"] = False
        tc.variables["GTSAM_WRAP_SERIALIZATION"] = self.options.wrap_serialization
        tc.variables["GTSAM_INSTALL_MATLAB_TOOLBOX"] = self.options.install_matlab_toolbox
        tc.variables["GTSAM_INSTALL_CYTHON_TOOLBOX"] = self.options.install_cython_toolbox
        tc.variables["GTSAM_INSTALL_CPPUNITLITE"] = self.options.install_cppunitlite
        tc.variables["GTSAM_INSTALL_GEOGRAPHICLIB"] = False
        tc.variables["GTSAM_USE_SYSTEM_EIGEN"] = True
        tc.variables["GTSAM_BUILD_TYPE_POSTFIXES"] = False
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

        prefix = "lib" if is_msvc(self) and not self.options.shared else ""

        self.cpp_info.components["libgtsam"].set_property("cmake_target_name", "gtsam")
        self.cpp_info.components["libgtsam"].libs = [f"{prefix}gtsam"]
        self.cpp_info.components["libgtsam"].requires = [f"boost::{component}" for component in self._required_boost_components]
        self.cpp_info.components["libgtsam"].requires.append("eigen::eigen")
        if self.options.with_TBB:
            self.cpp_info.components["libgtsam"].requires.append("onetbb::onetbb")
        if self.options.support_nested_dissection:
            self.cpp_info.components["libgtsam"].requires.append("libmetis-gtsam")
        if self.settings.os == "Windows" and Version(self.version) >= "4.0.3":
            self.cpp_info.components["libgtsam"].system_libs = ["dbghelp"]

        if self.options.build_unstable:
            self.cpp_info.components["libgtsam_unstable"].set_property("cmake_target_name", "gtsam_unstable")
            self.cpp_info.components["libgtsam_unstable"].libs = [f"{prefix}gtsam_unstable"]
            self.cpp_info.components["libgtsam_unstable"].requires = ["libgtsam"]

        if self.options.support_nested_dissection:
            self.cpp_info.components["libmetis-gtsam"].set_property("cmake_target_name", "metis-gtsam")
            self.cpp_info.components["libmetis-gtsam"].libs = ["metis-gtsam"]
            self.cpp_info.components["libmetis-gtsam"].names["pkg_config"] = "metis-gtsam"

        if self.options.install_cppunitlite:
            self.cpp_info.components["gtsam_CppUnitLite"].set_property("cmake_target_name", "CppUnitLite")
            self.cpp_info.components["gtsam_CppUnitLite"].libs = ["CppUnitLite"]
            self.cpp_info.components["gtsam_CppUnitLite"].requires = ["boost::boost"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "GTSAM"
        self.cpp_info.names["cmake_find_package_multi"] = "GTSAM"
        self.cpp_info.components["libgtsam"].names["cmake_find_package"] = "gtsam"
        self.cpp_info.components["libgtsam"].names["cmake_find_package_multi"] = "gtsam"
        self.cpp_info.components["libgtsam"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["libgtsam"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.build_unstable:
            self.cpp_info.components["libgtsam_unstable"].names["cmake_find_package"] = "gtsam_unstable"
            self.cpp_info.components["libgtsam_unstable"].names["cmake_find_package_multi"] = "gtsam_unstable"
            self.cpp_info.components["libgtsam_unstable"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["libgtsam_unstable"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.support_nested_dissection:
            self.cpp_info.components["libmetis-gtsam"].names["cmake_find_package"] = "metis-gtsam"
            self.cpp_info.components["libmetis-gtsam"].names["cmake_find_package_multi"] = "metis-gtsam"
            self.cpp_info.components["libmetis-gtsam"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["libmetis-gtsam"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        if self.options.install_cppunitlite:
            self.cpp_info.components["gtsam_CppUnitLite"].names["cmake_find_package"] = "CppUnitLite"
            self.cpp_info.components["gtsam_CppUnitLite"].names["cmake_find_package_multi"] = "CppUnitLite"
            self.cpp_info.components["gtsam_CppUnitLite"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
            self.cpp_info.components["gtsam_CppUnitLite"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
