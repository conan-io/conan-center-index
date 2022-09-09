import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rm, rmdir
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, is_msvc_static_runtime, check_min_vs
from conan.tools.scm import Version

required_conan_version = ">=1.50.0"


class GTestConan(ConanFile):
    name = "gtest"
    description = "Google's C++ test framework"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/googletest"
    topics = ("testing", "google-testing", "unit-test")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "build_gmock": [True, False],
        "fPIC": [True, False],
        "no_main": [True, False],
        "debug_postfix": ["ANY"],
        "hide_symbols": [True, False],
    }
    default_options = {
        "shared": False,
        "build_gmock": True,
        "fPIC": True,
        "no_main": False,
        "debug_postfix": "d",
        "hide_symbols": False,
    }

    @property
    def _minimum_cpp_standard(self):
        if self.version == "1.8.1":
            return 98
        else:
            return 11

    @property
    def _minimum_compilers_version(self):
        if self.version == "1.8.1":
            return {
                "Visual Studio": "14"
            }
        elif self.version == "1.10.0":
            return {
                "Visual Studio": "14",
                "gcc": "4.8.1",
                "clang": "3.3",
                "apple-clang": "5.0"
            }
        else:
            return {
                "Visual Studio": "14",
                "gcc": "5",
                "clang": "5",
                "apple-clang": "9.1"
            }

    @property
    def _is_clang_cl(self):
        return self.settings.os == "Windows" and self.settings.compiler == "clang"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, patch["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.build_type != "Debug":
            del self.options.debug_postfix

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def package_id(self):
        del self.info.options.no_main

    def validate(self):
        if is_msvc_static_runtime(self) and self.info.options.shared(self):
            raise ConanInvalidConfiguration(
                "gtest:shared=True with compiler=\"Visual Studio\" is not "
                "compatible with compiler.runtime=MT/MTd"
            )

        if self.info.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        compiler = self.info.settings.compiler
        min_version = self._minimum_compilers_version.get(str(compiler))
        if min_version and loose_lt_semver(str(compiler.version), min_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires {compiler} {min_version}. The current compiler is {compiler} {compiler.version}."
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
        # No warnings as errors
        internal_utils = os.path.join(self.source_folder, "googletest",
                                      "cmake", "internal_utils.cmake")
        replace_in_file(self, internal_utils, "-WX", "")
        if self.version == "cci.20210126" or Version(self.version) < "1.12.0":
            replace_in_file(self, internal_utils, "-Werror", "")

    def generate(self):
        tc = CMakeToolchain(self)

        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        
        if self.settings.build_type == "Debug":
            tc.cache_variables["CUSTOM_DEBUG_POSTFIX"] = str(self.options.debug_postfix)
        if is_msvc(self) or self._is_clang_cl:
            tc.cache_variables["gtest_force_shared_crt"] = "MD" in msvc_runtime_flag(self)

        try:
           check_min_vs(self, "191")
        except ConanInvalidConfiguration:
            tc.preprocessor_definitions["GTEST_LANG_CXX11"] = 1
            tc.preprocessor_definitions["GTEST_HAS_TR1_TUPLE"] = 0
            
        tc.cache_variables["BUILD_GMOCK"] = bool(self.options.build_gmock)
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            tc.cache_variables["gtest_disable_pthreads"] = True
        tc.cache_variables["gtest_hide_internal_symbols"] = bool(self.options.hide_symbols)
        tc.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))

    @property
    def _postfix(self):
        # In 1.12.0, gtest remove debug postfix.
        if self.version != "cci.20210126" and Version(self.version) >= "1.12.0":
            return ""
        return self.options.debug_postfix if self.settings.build_type == "Debug" else ""

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "GTest")

        # gtest
        self.cpp_info.components["libgtest"].set_property("cmake_target_name", "GTest::gtest")
        self.cpp_info.components["libgtest"].set_property("cmake_target_aliases", ["GTest::GTest"])
        self.cpp_info.components["libgtest"].set_property("pkg_config_name", "gtest")
        self.cpp_info.components["libgtest"].libs = [f"gtest{self._postfix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libgtest"].system_libs.append("m")
            self.cpp_info.components["libgtest"].system_libs.append("pthread")
        if self.settings.os == "Neutrino" and self.settings.os.version == "7.1":
            self.cpp_info.components["libgtest"].system_libs.append("regex")
        if self.options.shared:
            self.cpp_info.components["libgtest"].defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")
        if self.version == "1.8.1":
            if (self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) >= "15") or \
               (str(self.settings.compiler) == "msvc" and Version(self.settings.compiler.version) >= "191"):
                self.cpp_info.components["libgtest"].defines.append("GTEST_LANG_CXX11=1")
                self.cpp_info.components["libgtest"].defines.append("GTEST_HAS_TR1_TUPLE=0")

        # gtest_main
        if not self.options.no_main:
            self.cpp_info.components["gtest_main"].set_property("cmake_target_name", "GTest::gtest_main")
            self.cpp_info.components["gtest_main"].set_property("cmake_target_aliases", ["GTest::Main"])
            self.cpp_info.components["gtest_main"].set_property("pkg_config_name", "gtest_main")
            self.cpp_info.components["gtest_main"].libs = [f"gtest_main{self._postfix}"]
            self.cpp_info.components["gtest_main"].requires = ["libgtest"]

        # gmock
        if self.options.build_gmock:
            self.cpp_info.components["gmock"].set_property("cmake_target_name", "GTest::gmock")
            self.cpp_info.components["gmock"].set_property("pkg_config_name", "gmock")
            self.cpp_info.components["gmock"].libs = [f"gmock{self._postfix}"]
            self.cpp_info.components["gmock"].requires = ["libgtest"]

            # gmock_main
            if not self.options.no_main:
                self.cpp_info.components["gmock_main"].set_property("cmake_target_name", "GTest::gmock_main")
                self.cpp_info.components["gmock_main"].set_property("pkg_config_name", "gmock_main")
                self.cpp_info.components["gmock_main"].libs = [f"gmock_main{self._postfix}"]
                self.cpp_info.components["gmock_main"].requires = ["gmock"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "GTest"
        self.cpp_info.names["cmake_find_package_multi"] = "GTest"
        self.cpp_info.components["libgtest"].names["cmake_find_package"] = "gtest"
        self.cpp_info.components["libgtest"].names["cmake_find_package_multi"] = "gtest"
