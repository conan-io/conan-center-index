from conans import ConanFile, CMake, tools
import os
import shutil
import sys


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake", "cmake_find_package"

    @property
    def _conan_build_folder(self):
        return "conan_find_package"

    @property
    def _cmake_build_dir(self):
        return "cmake_find_package"

    def build(self):
        # Move the generated FindBoost.cmake to backup/FindBoost.cmake
        os.mkdir("backup")
        os.rename(src=os.path.join("FindBoost.cmake"), dst=os.path.join("backup", "FindBoost.cmake"))

        # Build using CMake's find_package
        # FIXME: disabled because recent boost versions require a recent cmake versions.
        # When a cmake version does not support a boost version, imported boost targets are disabled.
        # self._build_cmake(self._cmake_build_dir, False)

        # Copy the generated FindBoost.cmake back
        shutil.copy(src=os.path.join("backup", "FindBoost.cmake"), dst=os.path.join("FindBoost.cmake"))
        # Build using conan's find_package (generated with cmake_find_package)
        self._build_cmake(self._conan_build_folder, True)

    def _build_cmake(self, build_folder, conan_boost_findpackage):
        with tools.vcvars(self.settings) if (self.settings.os == "Windows" and self.settings.compiler == "clang") else tools.no_op():
            cmake = CMake(self)
            cmake.definitions["CONAN_INSTALL_FOLDER"] = self.build_folder
            cmake.definitions["Boost_ADDITIONAL_VERSIONS"] = self.deps_cpp_info["boost"].version
            cmake.definitions["HEADER_ONLY"] = self.options["boost"].header_only
            if not self.options["boost"].header_only:
                cmake.definitions["Boost_USE_STATIC_LIBS"] = not self.options["boost"].shared
            cmake.definitions["WITH_PYTHON"] = not self.options["boost"].without_python
            if not self.options["boost"].without_python:
                cmake.definitions["WITH_PYTHON"] = "TRUE"
                pyversion = tools.Version(self.options["boost"].python_version)
                cmake.definitions["Python_ADDITIONAL_VERSIONS"] = "{}.{}".format(pyversion.major, pyversion.minor)
                cmake.definitions["PYTHON_COMPONENT_SUFFIX"] = "{}{}".format(pyversion.major, pyversion.minor)
            cmake.definitions["WITH_RANDOM"] = not self.options["boost"].without_random
            cmake.definitions["WITH_REGEX"] = not self.options["boost"].without_regex
            cmake.definitions["WITH_TEST"] = not self.options["boost"].without_test
            cmake.definitions["WITH_COROUTINE"] = not self.options["boost"].without_coroutine
            cmake.definitions["WITH_CHRONO"] = not self.options["boost"].without_chrono
            cmake.definitions["Boost_NO_BOOST_CMAKE"] = True
            cmake.definitions["CONAN_BOOST_FINDPACKAGE"] = conan_boost_findpackage
            cmake.definitions["Boost_NO_BOOST_CMAKE"] = True
            cmake.configure(build_folder=build_folder)
            cmake.build()

    def test(self):
        if tools.cross_building(self.settings):
            return
        for subdir in (self._conan_build_folder, ): #(self._conan_build_folder, self._cmake_build_dir):
            bindir = os.path.join(subdir, "bin")
            libdir = os.path.join(subdir, "lib")
            self.run(os.path.join(bindir, "lambda_exe"), run_environment=True)
            if self.options["boost"].header_only:
                return
            if not self.options["boost"].without_random:
                self.run(os.path.join(bindir, "random_exe"), run_environment=True)
            if not self.options["boost"].without_regex:
                self.run(os.path.join(bindir, "regex_exe"), run_environment=True)
            if not self.options["boost"].without_test:
                self.run(os.path.join(bindir, "test_exe"), run_environment=True)
            if not self.options["boost"].without_coroutine:
                self.run(os.path.join(bindir, "coroutine_exe"), run_environment=True)
            if not self.options["boost"].without_chrono:
                self.run(os.path.join(bindir, "chrono_exe"), run_environment=True)
            if not self.options["boost"].without_python:
                with tools.environment_append({"PYTHONPATH": "{}:{}".format(bindir, libdir)}):
                    self.run("{} {}".format(sys.executable, os.path.join(self.source_folder, "python.py")), run_environment=True)
                self.run(os.path.join(bindir, "numpy_exe"), run_environment=True)
