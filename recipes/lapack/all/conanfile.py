import glob
import os
import shutil
from io import StringIO

from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy, get, rmdir


class LapackConan(ConanFile):
    name = "lapack"
    license = "BSD-3-Clause"
    homepage = "https://github.com/Reference-LAPACK/lapack"
    description = "Fortran subroutines for solving problems in numerical linear algebra"
    topics = "lapack"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def requirements(self):
        self.requires("zlib/1.2.12")
        # self.requires("gcc/12.2.0")

    def build_requirements(self):
        pass
        # self.tool_requires("gcc/12.2.0")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate_build(self):
        min_version = {
            "apple-clang": "8.0",
        }

        unsupported = ["Visual Studio", "msvc"]
        supported = ["gcc", "clang", "apple-clang"]

        if Version(self.info.settings.compiler.version.value) < min_version.get(
            str(self.info.settings.compiler), "0.0"
        ):
            raise ConanInvalidConfiguration(
                f"lapack requires {self.info.settings.compiler} >= {min_version[self.info.settings.compiler]}"
            )

        if self.settings.compiler in unsupported:
            raise ConanInvalidConfiguration(
                f"This library cannot be built with {self.info.settings.compiler}. Please use one of the "
                + f"following alternatives instead: {', '.join(supported)}"
            )

    def validate(self):
        if self.info.settings.os == "Windows" and not self.info.options.shared:
            raise ConanInvalidConfiguration(
                "Only shared builds are supported for Windows"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def generate(self):
        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

        # env = Environment()
        # env.define("FC", os.path.join(self.deps_cpp_info["gfortran"].bin_paths[0], "gfortran"))
        # envvars = env.vars(self, scope="build")
        # envvars.save_script("conanbuild_define_fortran_compiler")

        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_GNUtoMS"] = self.settings.os == "Windows"
        tc.cache_variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["LAPACKE"] = True
        tc.cache_variables["CBLAS"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        for target in ["blas", "cblas", "lapack", "lapacke"]:
            cmake.build(target=target)

    def package(self):

        cmake = CMake(self)
        cmake.configure()
        cmake.install()

        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        if self.settings.os == "Windows":
            # Copy MinGW dlls for Visual Studio consumers
            package_bin = os.path.join(self.package_folder, "bin")
            for bin_path in self.deps_cpp_info.bin_paths:
                copy(
                    self, pattern="*seh*.dll", dst=package_bin, src=bin_path, keep_path=False
                )
                copy(
                    self, pattern="*sjlj*.dll", dst=package_bin, src=bin_path, keep_path=False
                )
                copy(
                    self,
                    pattern="*dwarf2*.dll",
                    dst=package_bin,
                    src=bin_path,
                    keep_path=False,
                )
                copy(
                    self,
                    pattern="*quadmath*.dll",
                    dst=package_bin,
                    src=bin_path,
                    keep_path=False,
                )
                copy(
                    self,
                    pattern="*winpthread*.dll",
                    dst=package_bin,
                    src=bin_path,
                    keep_path=False,
                )
                copy(
                    self,
                    pattern="*gfortran*.dll",
                    dst=package_bin,
                    src=bin_path,
                    keep_path=False,
                )

            with tools.chdir(os.path.join(self.package_folder, "lib")):
                libs = glob.glob("lib*.a")
                for lib in libs:
                    vslib = lib[3:-2] + ".lib"
                    self.output.info(f"Renaming {lib} into {vslib}")
                    shutil.move(lib, vslib)

    def compatibility(self):
        if self.settings.compiler in ["Visual Studio", "msvc"]:
            return [{"settings": [("compiler", "gcc")]}]
            # compatible_pkg = self.info.clone()

            # compatible_pkg.settings.compiler = "gcc"
            # del compatible_pkg.settings.compiler.version
            # del compatible_pkg.settings.compiler.runtime
            # del compatible_pkg.settings.compiler.toolset

            # self.compatible_packages.append(compatible_pkg)

    def get_lib_name(self, lib):
        if self.settings.os == "Windows":
            lib = lib + ".dll.lib"
        return lib

    def package_info(self):

        self.cpp_info.set_property("cmake_file_name", "LAPACK")

        self.cpp_info.components["blas"].set_property("cmake_target_name", "BLAS::BLAS")
        self.cpp_info.components["blas"].libs = [self.get_lib_name("blas")]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["blas"].system_libs.extend(["gfortran"])

        self.cpp_info.components["cblas"].set_property("cmake_target_name", "BLAS::CBLAS")
        self.cpp_info.components["cblas"].libs = [self.get_lib_name("cblas")]
        self.cpp_info.components["cblas"].requires = ["blas"]

        self.cpp_info.components["lapack"].set_property("cmake_target_name", "LAPACK::LAPACK")
        self.cpp_info.components["lapack"].libs = [self.get_lib_name("lapack")]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["lapack"].system_libs.extend(["m"])
            self.cpp_info.components["lapack"].system_libs.extend(["gfortran"])
        self.cpp_info.components["lapack"].requires = ["blas"]
	
        self.cpp_info.components["lapacke"].set_property("cmake_target_name", "LAPACK::LAPACKE")
        self.cpp_info.components["lapacke"].libs = [self.get_lib_name("lapacke")]
        self.cpp_info.components["lapacke"].requires = ["lapack"]
