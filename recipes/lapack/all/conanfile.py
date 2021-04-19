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
    options = {"shared": [True, False], "fPIC": [True, False], "visual_studio": [True, False]}
    default_options = {"shared": False, "visual_studio": False, "fPIC": True}
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    requires = "zlib/1.2.11"
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Macos" and \
            self.settings.compiler == "apple-clang" and \
            Version(self.settings.compiler.version.value) < "8.0":
            raise ConanInvalidConfiguration("lapack requires apple-clang >=8.0")
        if self.options.visual_studio and not self.options.shared:
            raise ConanInvalidConfiguration("only shared builds are supported for Visual Studio")
        if self.settings.compiler == "Visual Studio" and not self.options.visual_studio:
            raise ConanInvalidConfiguration("This library needs option 'visual_studio=True' to be consumed")

    def config_options(self):
        if self.options.shared or self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_GNUtoMS"] = self.options.visual_studio
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["LAPACKE"] = True
        cmake.definitions["CBLAS"] = True
        cmake.configure(build_dir=self._build_subfolder)
        return cmake

    def build(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("This library cannot be built with Visual Studio. Please use MinGW to "
                            "build it and option 'visual_studio=True' to build and consume.")
        cmake = self._configure_cmake()
        for target in ["blas", "cblas", "lapack", "lapacke"]:
            cmake.build(target=target)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        if self.options.visual_studio:
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
        if self.options.visual_studio:
            self.info.settings.compiler = "Visual Studio"
            del self.info.settings.compiler.version
            del self.info.settings.compiler.runtime
            del self.info.settings.compiler.toolset

    def package_info(self):
        # the order is important for static builds
        self.cpp_info.libs = ["lapacke", "lapack", "blas", "cblas"]
        self.cpp_info.system_libs.extend(["gfortran", "m"])
        if self.options.visual_studio and self.options.shared:
            self.cpp_info.libs = ["lapacke.dll.lib", "lapack.dll.lib", "blas.dll.lib", "cblas.dll.lib"]
        self.cpp_info.libdirs = ["lib"]
        if tools.os_info.is_macos:
            brewout = StringIO()
            try:
                self.run("gfortran --print-file-name libgfortran.dylib", output=brewout)
            except Exception as error:
                raise ConanException("Failed to run command: {}. Output: {}".format(error, brewout.getvalue()))
            lib = os.path.dirname(os.path.normpath(brewout.getvalue().strip()))
            self.cpp_info.libdirs.append(lib)
