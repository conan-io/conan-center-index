import os
from conans import ConanFile, CMake, tools


class CAresConan(ConanFile):
    name = "c-ares"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A C library for asynchronous DNS requests"
    topics = ("conan", "c-ares", "dns")
    homepage = "https://c-ares.haxx.se/"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}
    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("c-ares-cares-{}".format(self.version.replace(".", "_")), "source_folder")

    def _cmake_configure(self):
        cmake = CMake(self)
        cmake.definitions["CARES_STATIC"] = not self.options.shared
        cmake.definitions["CARES_SHARED"] = self.options.shared
        cmake.definitions["CARES_BUILD_TESTS"] = "OFF"
        cmake.definitions["CARES_MSVC_STATIC_RUNTIME"] = "OFF"
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._cmake_configure()
        cmake.build()
        cmake.install()

    def package(self):
        cmake = self._cmake_configure()
        cmake.install()
        self.copy("*LICENSE.md", src=self.source_folder, dst="licenses", keep_path=False)

        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append("CARES_STATICLIB")
        if self.settings.os == "Windows":
            self.cpp_info.libs.append("ws2_32")
