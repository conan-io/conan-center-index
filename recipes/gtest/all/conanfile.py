from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import is_msvc_static_runtime, msvc_runtime_flag
from conan.tools.scm import Version
import os

required_conan_version = ">=2.1"


class GTestConan(ConanFile):
    name = "gtest"
    description = "Google's C++ test framework"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/googletest"
    topics = ("testing", "google-testing", "unit-test")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_gmock": [True, False],
        "no_main": [True, False],
        "hide_symbols": [True, False],
        "disable_pthreads": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_gmock": True,
        "no_main": False,
        "hide_symbols": False,
        "disable_pthreads": False,
    }
    # disallow cppstd compatibility, as it affects the ABI in this library
    # see https://github.com/conan-io/conan-center-index/issues/23854
    extension_properties = {"compatibility_cppstd": False}
    implements = ["auto_shared_fpic"]

    @property
    def _min_cppstd(self):
        if Version(self.version) < "1.13.0":
            return 11
        elif Version(self.version) < "1.17.0":
            return "14"
        return "17"

    @property
    def _minimum_compilers_version(self):
        return {
            "11": {
                "Visual Studio": "14",
                "msvc": "190",
                "gcc": "5",
                "clang": "5",
                "apple-clang": "9.1",
            },
            # Sinse 1.13.0, gtest requires C++14 and Google's Foundational C++ Support Policy
            # https://github.com/google/oss-policies-info/blob/603a042ce2ee8f165fac46721a651d796ce59cb6/foundational-cxx-support-matrix.md
            "14": {
                "Visual Studio": "15",
                "msvc": "191",
                "gcc": "7.3.1",
                "clang": "6",
                "apple-clang": "12",
            },
        }.get(self._min_cppstd, {})

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        del self.info.options.no_main # Only used to expose more targets

    def validate(self):
        if self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("gtest shared is not compatible with static vc runtime")

        check_min_cppstd(self, self._min_cppstd)

        compiler = self.settings.compiler
        min_version = self._minimum_compilers_version.get(str(compiler))
        if min_version and Version(compiler.version) < min_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        self._patch_sources()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_GMOCK"] = bool(self.options.build_gmock)
        tc.variables["gtest_hide_internal_symbols"] = bool(self.options.hide_symbols)

        if self.settings.compiler.get_safe("runtime"):
            tc.variables["gtest_force_shared_crt"] = "MD" in msvc_runtime_flag(self)
        tc.variables["gtest_disable_pthreads"] = self.options.disable_pthreads
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # No warnings as errors
        internal_utils = os.path.join(self.source_folder, "googletest", "cmake", "internal_utils.cmake")
        replace_in_file(self, internal_utils, "-WX", "")

    def build_requirements(self):
        if Version(self.version) >= "1.17.0":
            self.tool_requires("cmake/[>=3.16 <4]")

    def build(self):
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

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "GTest")

        # gtest
        self.cpp_info.components["libgtest"].set_property("cmake_target_name", "GTest::gtest")
        self.cpp_info.components["libgtest"].set_property("cmake_target_aliases", ["GTest::GTest"])
        self.cpp_info.components["libgtest"].set_property("pkg_config_name", "gtest")
        self.cpp_info.components["libgtest"].libs = ["gtest"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libgtest"].system_libs.append("m")
            if not self.options.disable_pthreads:
                self.cpp_info.components["libgtest"].system_libs.append("pthread")
        if self.settings.os == "Neutrino" and self.settings.os.version == "7.1":
            self.cpp_info.components["libgtest"].system_libs.append("regex")
        if self.options.shared:
            self.cpp_info.components["libgtest"].defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")

        # gtest_main
        if not self.options.no_main:
            self.cpp_info.components["gtest_main"].set_property("cmake_target_name", "GTest::gtest_main")
            self.cpp_info.components["gtest_main"].set_property("cmake_target_aliases", ["GTest::Main"])
            self.cpp_info.components["gtest_main"].set_property("pkg_config_name", "gtest_main")
            self.cpp_info.components["gtest_main"].libs = ["gtest_main"]
            self.cpp_info.components["gtest_main"].requires = ["libgtest"]

        # gmock
        if self.options.build_gmock:
            self.cpp_info.components["gmock"].set_property("cmake_target_name", "GTest::gmock")
            self.cpp_info.components["gmock"].set_property("pkg_config_name", "gmock")
            self.cpp_info.components["gmock"].libs = ["gmock"]
            self.cpp_info.components["gmock"].requires = ["libgtest"]

            # gmock_main
            if not self.options.no_main:
                self.cpp_info.components["gmock_main"].set_property("cmake_target_name", "GTest::gmock_main")
                self.cpp_info.components["gmock_main"].set_property("pkg_config_name", "gmock_main")
                self.cpp_info.components["gmock_main"].libs = ["gmock_main"]
                self.cpp_info.components["gmock_main"].requires = ["gmock"]
