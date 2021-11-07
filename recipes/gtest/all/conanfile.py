from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import functools

required_conan_version = ">=1.36.0"


class GTestConan(ConanFile):
    name = "gtest"
    description = "Google's C++ test framework"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/googletest"
    license = "BSD-3-Clause"
    topics = ("testing", "google-testing", "unit-test")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "build_gmock": [True, False],
        "fPIC": [True, False],
        "no_main": [True, False],
        "debug_postfix": "ANY",
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

    exports_sources = "CMakeLists.txt", "patches/*"
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.build_type != "Debug":
            del self.options.debug_postfix

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if self.settings.compiler == "Visual Studio":
            if self.options.shared and "MT" in self.settings.compiler.runtime:
                raise ConanInvalidConfiguration("gtest:shared=True with compiler=\"Visual Studio\" is not compatible with compiler.runtime=MT/MTd")

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        if not min_version:
            self.output.warn("{} recipe lacks information about {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if lazy_lt_semver(str(self.settings.compiler.version), min_version):
                raise ConanInvalidConfiguration("{0} requires {1} {2}. The current compiler is {1} {3}.".format(
                    self.name, self.settings.compiler, min_version, self.settings.compiler.version))

    def package_id(self):
        del self.info.options.no_main

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        if self.settings.build_type == "Debug":
            cmake.definitions["CUSTOM_DEBUG_POSTFIX"] = self.options.debug_postfix
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["gtest_force_shared_crt"] = "MD" in self.settings.compiler.runtime
        cmake.definitions["BUILD_GMOCK"] = self.options.build_gmock
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            cmake.definitions["gtest_disable_pthreads"] = True
        cmake.definitions["gtest_hide_internal_symbols"] = self.options.hide_symbols
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")

    @property
    def _postfix(self):
        return self.options.debug_postfix if self.settings.build_type == "Debug" else ""

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "GTest")
        self.cpp_info.set_property("cmake_target_name", "GTest")
        self.cpp_info.components["libgtest"].set_property("cmake_target_name", "gtest")
        self.cpp_info.components["libgtest"].set_property("pkg_config_name", "gtest")
        self.cpp_info.components["libgtest"].libs = ["gtest{}".format(self._postfix)]
        if self.settings.os == "Linux":
            self.cpp_info.components["libgtest"].system_libs.append("pthread")

        if self.settings.os == "Neutrino" and self.settings.os.version == "7.1":
            self.cpp_info.components["libgtest"].system_libs.append("regex")

        if self.options.shared:
            self.cpp_info.components["libgtest"].defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")

        if self.version == "1.8.1":
            if self.settings.compiler == "Visual Studio":
                if tools.Version(self.settings.compiler.version) >= "15":
                    self.cpp_info.components["libgtest"].defines.append("GTEST_LANG_CXX11=1")
                    self.cpp_info.components["libgtest"].defines.append("GTEST_HAS_TR1_TUPLE=0")

        if not self.options.no_main:
            self.cpp_info.components["gtest_main"].set_property("cmake_target_name", "gtest_main")
            self.cpp_info.components["gtest_main"].set_property("pkg_config_name", "gtest_main")
            self.cpp_info.components["gtest_main"].libs = ["gtest_main{}".format(self._postfix)]
            self.cpp_info.components["gtest_main"].requires = ["libgtest"]

        if self.options.build_gmock:
            self.cpp_info.components["gmock"].set_property("cmake_target_name", "gmock")
            self.cpp_info.components["gmock"].set_property("pkg_config_name", "gmock")
            self.cpp_info.components["gmock"].libs = ["gmock{}".format(self._postfix)]
            self.cpp_info.components["gmock"].requires = ["libgtest"]
            if not self.options.no_main:
                self.cpp_info.components["gmock_main"].set_property("cmake_target_name", "gmock_main")
                self.cpp_info.components["gmock_main"].set_property("pkg_config_name", "gmock_main")
                self.cpp_info.components["gmock_main"].libs = ["gmock_main{}".format(self._postfix)]
                self.cpp_info.components["gmock_main"].requires = ["gmock"]
