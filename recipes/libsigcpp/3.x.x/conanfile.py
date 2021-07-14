import glob
import os
import shutil

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


required_conan_version = ">=1.33.0"


class LibSigCppConan(ConanFile):
    name = "libsigcpp"
    homepage = "https://github.com/libsigcplusplus/libsigcplusplus"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-3.0"
    description = "libsigc++ implements a typesafe callback system for standard C++."
    topics = ("conan", "libsigcpp", "callback")
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _has_support_for_cpp17(self):
        supported_compilers = [("apple-clang", 10), ("clang", 6), ("gcc", 7), ("Visual Studio", 15.7)]
        compiler, version = self.settings.compiler, tools.Version(self.settings.compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
           tools.check_min_cppstd(self, 17)
        if not self._has_support_for_cpp17():
            raise ConanInvalidConfiguration("This library requires C++17 or higher support standard."
                                            " {} {} is not supported."
                                            .format(self.settings.compiler,
                                                    self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if not self.options.shared:
            tools.replace_in_file(os.path.join(self._source_subfolder, "sigc++config.h.cmake"),
                                  "define SIGC_DLL 1", "undef SIGC_DLL")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        for header_file in glob.glob(os.path.join(self.package_folder, "lib", "sigc++-3.0", "include", "*.h")):
            shutil.move(
                header_file,
                os.path.join(self.package_folder, "include", "sigc++-3.0", os.path.basename(header_file))
            )
        for dir_to_remove in ["cmake", "pkgconfig", "sigc++-3.0"]:
            tools.rmdir(os.path.join(self.package_folder, "lib", dir_to_remove))

    def package_info(self):
        # TODO: CMake imported target shouldn't be namespaced
        self.cpp_info.names["cmake_find_package"] = "sigc++-3"
        self.cpp_info.names["cmake_find_package_multi"] = "sigc++-3"
        self.cpp_info.names["pkg_config"] = "sigc++-3.0"
        self.cpp_info.components["sigc++"].names["cmake_find_package"] = "sigc-3.0"
        self.cpp_info.components["sigc++"].names["cmake_find_package_multi"] = "sigc-3.0"
        self.cpp_info.components["sigc++"].includedirs = [os.path.join("include", "sigc++-3.0")]
        self.cpp_info.components["sigc++"].libs = tools.collect_libs(self)
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["sigc++"].system_libs.append("m")
