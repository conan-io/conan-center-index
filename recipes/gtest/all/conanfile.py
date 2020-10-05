import glob
import os
from conans import ConanFile, CMake, tools
from conans.model.version import Version
from conans.errors import ConanInvalidConfiguration


class GTestConan(ConanFile):
    name = "gtest"
    description = "Google's C++ test framework"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/googletest"
    license = "BSD-3-Clause"
    topics = ("conan", "gtest", "testing", "google-testing", "unit-test")
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "build_gmock": [True, False], "fPIC": [True, False], "no_main": [True, False], "debug_postfix": "ANY", "hide_symbols": [True, False]}
    default_options = {"shared": False, "build_gmock": True, "fPIC": True, "no_main": False, "debug_postfix": 'd', "hide_symbols": False}
    _source_subfolder = "source_subfolder"

    @property
    def _postfix(self):
        return self.options.debug_postfix if self.settings.build_type == "Debug" else ""

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.build_type != "Debug":
            del self.options.debug_postfix

    def configure(self):
        if self.settings.os == "Windows":
            if self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version.value) <= "12":
                raise ConanInvalidConfiguration("Google Test {} does not support Visual Studio <= 12".format(self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "googletest-release-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        if self.settings.build_type == "Debug":
            cmake.definitions["CUSTOM_DEBUG_POSTFIX"] = self.options.debug_postfix
        if self.settings.os == "Windows" and self.settings.get_safe("compiler.runtime"):
            cmake.definitions["gtest_force_shared_crt"] = "MD" in str(self.settings.compiler.runtime)
        cmake.definitions["BUILD_GMOCK"] = self.options.build_gmock
        cmake.definitions["GTEST_NO_MAIN"] = self.options.no_main
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            cmake.definitions["gtest_disable_pthreads"] = True
        cmake.definitions["gtest_hide_internal_symbols"] = self.options.hide_symbols
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        for pdb_file in glob.glob(os.path.join(self.package_folder, "lib", "*.pdb")):
            os.unlink(pdb_file)

    def package_id(self):
        del self.info.options.no_main

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "GTest"
        self.cpp_info.names["cmake_find_package_multi"] = "GTest"
        self.cpp_info.components["libgtest"].names["cmake_find_package"] = "gtest"
        self.cpp_info.components["libgtest"].names["cmake_find_package_multi"] = "gtest"
        self.cpp_info.components["libgtest"].libs = ["gtest{}".format(self._postfix)]
        if self.settings.os == "Linux":
            self.cpp_info.components["libgtest"].system_libs.append("pthread")

        if self.options.shared:
            self.cpp_info.components["libgtest"].defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")

        if self.settings.compiler == "Visual Studio":
            if Version(self.settings.compiler.version.value) >= "15":
                self.cpp_info.components["libgtest"].defines.append("GTEST_LANG_CXX11=1")
                self.cpp_info.components["libgtest"].defines.append("GTEST_HAS_TR1_TUPLE=0")

        if not self.options.no_main:
            self.cpp_info.components["gtest_main"].libs = ["gtest_main{}".format(self._postfix)]
            self.cpp_info.components["gtest_main"].requires = ["libgtest"]

        if self.options.build_gmock:
            self.cpp_info.components["gmock"].libs = ["gmock{}".format(self._postfix)]
            self.cpp_info.components["gmock"].requires = ["libgtest"]
            if not self.options.no_main:
                self.cpp_info.components["gmock_main"].libs = ["gmock_main{}".format(self._postfix)]
                self.cpp_info.components["gmock_main"].requires = ["gmock"]
