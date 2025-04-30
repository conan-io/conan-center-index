from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
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
        "debug_postfix": ["ANY"],
        "disable_pthreads": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_gmock": True,
        "no_main": False,
        "hide_symbols": False,
        "debug_postfix": "d",
        "disable_pthreads": False,
    }
    # disallow cppstd compatibility, as it affects the ABI in this library
    # see https://github.com/conan-io/conan-center-index/issues/23854
    # Requires Conan >=1.53.0 <2 || >=2.1.0 to work
    extension_properties = {"compatibility_cppstd": False}

    @property
    def _min_cppstd(self):
        return "11" if Version(self.version) < "1.13.0" else "14"

    @property
    def _minimum_compilers_version(self):
        return {
            "11": {
                "Visual Studio": "14",
                "msvc": "190",
                "gcc": "4.8.1" if Version(self.version) < "1.11.0" else "5",
                "clang": "3.3" if Version(self.version) < "1.11.0" else "5",
                "apple-clang": "5.0" if Version(self.version) < "1.11.0" else "9.1",
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) >= "1.12.0" or self.settings.build_type != "Debug":
            del self.options.debug_postfix

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        del self.info.options.no_main # Only used to expose more targets

    def validate(self):
        if self.options.shared and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("gtest shared is not compatible with static vc runtime")

        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        compiler = self.settings.compiler
        min_version = self._minimum_compilers_version.get(str(compiler))
        if min_version and loose_lt_semver(str(compiler.version), min_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_GMOCK"] = bool(self.options.build_gmock)
        tc.variables["gtest_hide_internal_symbols"] = bool(self.options.hide_symbols)

        if self.settings.build_type == "Debug" and Version(self.version) < "1.12.0":
            tc.cache_variables["CUSTOM_DEBUG_POSTFIX"] = str(self.options.debug_postfix)

        if self.settings.compiler.get_safe("runtime"):
            tc.variables["gtest_force_shared_crt"] = "MD" in msvc_runtime_flag(self)
        tc.variables["gtest_disable_pthreads"] = self.options.disable_pthreads
        if Version(self.version) < "1.12.0":
            # Relocatable shared lib on Macos
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
            tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # No warnings as errors
        internal_utils = os.path.join(self.source_folder, "googletest", "cmake", "internal_utils.cmake")
        replace_in_file(self, internal_utils, "-WX", "")
        if Version(self.version) < "1.12.0":
            replace_in_file(self, internal_utils, "-Werror", "")

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
        return self.options.get_safe("debug_postfix", "")

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
