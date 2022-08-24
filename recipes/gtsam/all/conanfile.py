from conan.tools.microsoft import msvc_runtime_flag, is_msvc
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


class GtsamConan(ConanFile):
    name = "gtsam"
    license = "BSD-3-Clause"
    homepage = "https://github.com/borglab/gtsam"
    url = "https://github.com/conan-io/conan-center-index"
    description = ("GTSAM is a library of C++ classes that implement\
                    smoothing and mapping (SAM) in robotics and vision")
    topics = ("gtsam", "mapping", "smoothing")

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

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.options.with_TBB:
            self.options["onetbb"].tbbmalloc = True

    def requirements(self):
        self.requires("boost/1.78.0")
        self.requires("eigen/3.4.0")
        if self.options.with_TBB:
            self.requires("onetbb/2020.3")

    @property
    def _required_boost_components(self):
        return ["serialization", "system", "filesystem", "thread", "date_time", "regex", "timer", "chrono"]

    def validate(self):
        miss_boost_required_comp = any(getattr(self.options["boost"], "without_{}".format(boost_comp), True) for boost_comp in self._required_boost_components)
        if self.options["boost"].header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration(
                "{0} requires non header-only boost with these components: {1}".format(
                    self.name, ", ".join(self._required_boost_components)
                )
            )

        if self.options.with_TBB and not self.options["onetbb"].tbbmalloc:
            raise ConanInvalidConfiguration("gtsam with tbb requires onetbb:tbbmalloc=True")

        if is_msvc(self) and tools.Version(self.settings.compiler.version) < 15:
            raise ConanInvalidConfiguration ("GTSAM requires MSVC >= 15")

        if is_msvc(self) and tools.Version(self.version) >= '4.1' \
                and self.options.shared:
            raise ConanInvalidConfiguration("GTSAM does not support shared builds on MSVC. see https://github.com/borglab/gtsam/issues/1087")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        if is_msvc(self):
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "cmake", "GtsamBuildTypes.cmake"),
                                  "/MD ",
                                  "/{} ".format(msvc_runtime_flag(self)))
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "cmake", "GtsamBuildTypes.cmake"),
                                  "/MDd ",
                                  "/{} ".format(msvc_runtime_flag(self)))

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.definitions["GTSAM_USE_QUATERNIONS"] = self.options.use_quaternions
        self._cmake.definitions["GTSAM_POSE3_EXPMAP"] = self.options.pose3_expmap
        self._cmake.definitions["GTSAM_ROT3_EXPMAP"] = self.options.rot3_expmap
        self._cmake.definitions["GTSAM_ENABLE_CONSISTENCY_CHECKS"] = self.options.enable_consistency_checks
        self._cmake.definitions["GTSAM_WITH_TBB"] = self.options.with_TBB
        self._cmake.definitions["GTSAM_WITH_EIGEN_MKL"] = self.options.with_eigen_MKL
        self._cmake.definitions["GTSAM_WITH_EIGEN_MKL_OPENMP"] = self.options.with_eigen_MKL_OPENMP
        self._cmake.definitions["GTSAM_THROW_CHEIRALITY_EXCEPTION"] = self.options.throw_cheirality_exception
        self._cmake.definitions["GTSAM_ALLOW_DEPRECATED_SINCE_V4"] = self.options.allow_deprecated_since_V4
        self._cmake.definitions["GTSAM_TYPEDEF_POINTS_TO_VECTORS"] = self.options.typedef_points_to_vectors
        self._cmake.definitions["GTSAM_SUPPORT_NESTED_DISSECTION"] = self.options.support_nested_dissection
        self._cmake.definitions["GTSAM_TANGENT_PREINTEGRATION"] = self.options.tangent_preintegration
        self._cmake.definitions["GTSAM_BUILD_UNSTABLE"] = self.options.build_unstable
        self._cmake.definitions["GTSAM_DISABLE_NEW_TIMERS"] = self.options.disable_new_timers
        self._cmake.definitions["GTSAM_BUILD_TYPE_POSTFIXES"] = self.options.build_type_postfixes
        self._cmake.definitions["GTSAM_BUILD_TESTS"] = False
        self._cmake.definitions["Boost_USE_STATIC_LIBS"] = not self.options["boost"].shared
        self._cmake.definitions["Boost_NO_SYSTEM_PATHS"] = True
        self._cmake.definitions["GTSAM_BUILD_DOCS"] = False
        self._cmake.definitions["GTSAM_BUILD_DOC_HTML"] = False
        self._cmake.definitions["GTSAM_BUILD_EXAMPLES_ALWAYS"] = False
        self._cmake.definitions["GTSAM_BUILD_WRAP"] = self.options.build_wrap
        self._cmake.definitions["GTSAM_BUILD_WITH_MARCH_NATIVE"] = False
        self._cmake.definitions["GTSAM_WRAP_SERIALIZATION"] = self.options.wrap_serialization
        self._cmake.definitions["GTSAM_INSTALL_MATLAB_TOOLBOX"] = self.options.install_matlab_toolbox
        self._cmake.definitions["GTSAM_INSTALL_CYTHON_TOOLBOX"] = self.options.install_cython_toolbox
        self._cmake.definitions["GTSAM_INSTALL_CPPUNITLITE"] = self.options.install_cppunitlite
        self._cmake.definitions["GTSAM_INSTALL_GEOGRAPHICLIB"] = False
        self._cmake.definitions["GTSAM_USE_SYSTEM_EIGEN"] = True #Set to false to use eigen sources contained in GTSAM
        self._cmake.definitions["GTSAM_BUILD_TYPE_POSTFIXES"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("LICENSE.BSD", src=self._source_subfolder, dst="licenses")
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "CMake"))

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

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.files.save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "GTSAM")

        prefix = "lib" if is_msvc(self) and not self.options.shared else ""

        self.cpp_info.components["libgtsam"].set_property("cmake_target_name", "gtsam")
        self.cpp_info.components["libgtsam"].libs = ["{}gtsam".format(prefix)]
        self.cpp_info.components["libgtsam"].requires = ["boost::{}".format(component) for component in self._required_boost_components]
        self.cpp_info.components["libgtsam"].requires.append("eigen::eigen")
        if self.options.with_TBB:
            self.cpp_info.components["libgtsam"].requires.append("onetbb::onetbb")
        if self.options.support_nested_dissection:
            self.cpp_info.components["libgtsam"].requires.append("libmetis-gtsam")
        if self.settings.os == "Windows" and tools.Version(self.version) >= "4.0.3":
            self.cpp_info.components["libgtsam"].system_libs = ["dbghelp"]

        if self.options.build_unstable:
            self.cpp_info.components["libgtsam_unstable"].set_property("cmake_target_name", "gtsam_unstable")
            self.cpp_info.components["libgtsam_unstable"].libs = ["{}gtsam_unstable".format(prefix)]
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
