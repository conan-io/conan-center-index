import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version


class LibSigCppConan(ConanFile):
    name = "libsigcpp"
    version = "3.0.0"
    homepage = "https://github.com/libsigcplusplus/libsigcplusplus"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-3.0"
    description = "libsigc++ implements a typesafe callback system for standard C++."
    topics = ("conan", "libsigcpp", "callback")
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    exports_sources = ["CMakeLists.txt", "*.patch"]
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _supported_cppstd(self):
        return ["17", "gnu17", "20", "gnu20"]

    def _has_support_for_cpp17(self):
        supported_compilers = [("apple-clang", 10), ("clang", 6), ("gcc", 7), ("Visual Studio", 15.7)]
        compiler, version = self.settings.compiler, Version(self.settings.compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        compiler_version = Version(self.settings.compiler.version)
        if not self.options.shared:
            raise ConanInvalidConfiguration("This library supported shared option only")
        if self.settings.compiler.cppstd and \
           not self.settings.compiler.cppstd in self._supported_cppstd:
          raise ConanInvalidConfiguration("This library requires c++17 standard or higher."
                                          " {} required."
                                          .format(self.settings.compiler.cppstd))

        if not self._has_support_for_cpp17():
            raise ConanInvalidConfiguration("This library requires C++17 or higher support standard."
                                            " {} {} is not supported."
                                            .format(self.settings.compiler,
                                                    self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "libsigc++-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
        self.cpp_info.includedirs.extend([os.path.join('include', "sigc++-3.0"),
                                          os.path.join('lib', "sigc++-3.0", "include")])
