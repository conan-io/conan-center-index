import glob
import os
import shutil
from io import StringIO

from conans import ConanFile, CMake, tools
from conans.errors import ConanException
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class LapackConan(ConanFile):
    name = "lapack"
    license = "BSD-3-Clause"
    homepage = "https://github.com/Reference-LAPACK/lapack"
    description = "Fortran subroutines for solving problems in numerical linear algebra"
    topics = (
        "lapack"
    )
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    requires = "zlib/1.2.11"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    _cmake = None


    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Macos" and \
            self.settings.compiler == "apple-clang" and \
            Version(self.settings.compiler.version.value) < "8.0":
            raise ConanInvalidConfiguration("lapack requires apple-clang >=8.0")
        if self.settings.os == "Windows" and not self.options.shared:
            raise ConanInvalidConfiguration("only shared builds are supported for Windows")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CMAKE_GNUtoMS"] = self.settings.os == "Windows"
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["LAPACKE"] = True
        self._cmake.definitions["CBLAS"] = True
        self._cmake.configure(build_dir=self._build_subfolder)
        return self._cmake

    def build(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("This library cannot be built with Visual Studio. Please use MinGW to "
                            "build it.")
        self._cmake = self._configure_cmake()
        for target in ["blas", "cblas", "lapack", "lapacke"]:
            self._cmake.build(target=target)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self._cmake = self._configure_cmake()
        self._cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        if self.settings.os == "Windows":
            for bin_path in self.deps_cpp_info.bin_paths:  # Copy MinGW dlls for Visual Studio consumers
                self.copy(pattern="*seh*.dll", dst="bin", src=bin_path, keep_path=False)
                self.copy(pattern="*sjlj*.dll", dst="bin", src=bin_path, keep_path=False)
                self.copy(pattern="*dwarf2*.dll", dst="bin", src=bin_path, keep_path=False)
                self.copy(pattern="*quadmath*.dll", dst="bin", src=bin_path, keep_path=False)
                self.copy(pattern="*winpthread*.dll", dst="bin", src=bin_path, keep_path=False)
                self.copy(pattern="*gfortran*.dll", dst="bin", src=bin_path, keep_path=False)

            with tools.chdir(os.path.join(self.package_folder, "lib")):
                libs = glob.glob("lib*.a")
                for lib in libs:
                    vslib = lib[3:-2] + ".lib"
                    self.output.info('renaming %s into %s' % (lib, vslib))
                    shutil.move(lib, vslib)

    def package_id(self):
        if self.settings.compiler == "Visual Studio":
            compatible_pkg = self.info.clone() 

            compatible_pkg.settings.compiler = "gcc"
            del compatible_pkg.settings.compiler.version
            del compatible_pkg.settings.compiler.runtime
            del compatible_pkg.settings.compiler.toolset

            self.compatible_packages.append(compatible_pkg) 

    def package_info(self):
        # the order is important for static builds
        libs = ["lapacke", "lapack", "blas", "cblas"]
        if self.settings.os == "Windows":
            libs = [l + ".dll.lib" for l in libs]
        self.cpp_info.libs = libs

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["gfortran", "m"])
