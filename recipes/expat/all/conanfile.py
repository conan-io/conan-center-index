from conans import ConanFile, CMake, tools
from conans.tools import Version
import os


class ExpatConan(ConanFile):
    name = "expat"
    description = "Recipe for Expat library"
    topics = ("conan", "expat", "xml", "parsing")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libexpat/libexpat"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    exports_sources = ["CMakeLists.txt"]

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self, parallel=True)
        if Version(self.version) < "2.2.8":
            cmake.definitions["BUILD_doc"] = "Off"
            cmake.definitions["BUILD_examples"] =  "Off"
            cmake.definitions["BUILD_shared"] = self.options.shared
            cmake.definitions["BUILD_tests"] = "Off"
            cmake.definitions["BUILD_tools"] = "Off"
        else:
            # These options were renamed in 2.2.8 to be more consistent
            cmake.definitions["EXPAT_BUILD_DOCS"] = "Off"
            cmake.definitions["EXPAT_BUILD_EXAMPLES"] =  "Off"
            cmake.definitions["EXPAT_SHARED_LIBS"] = self.options.shared
            cmake.definitions["EXPAT_BUILD_TESTS"] = "Off"
            cmake.definitions["EXPAT_BUILD_TOOLS"] = "Off"

        cmake.configure(build_folder=self._build_subfolder)
        return cmake 

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "EXPAT"
        self.cpp_info.names["cmake_find_package_multi"] = "EXPAT"
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["XML_STATIC"]
