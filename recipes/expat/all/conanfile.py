from conans import ConanFile, CMake, tools
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
        cmake.definitions["BUILD_doc"] = "Off"
        cmake.definitions["BUILD_examples"] =  "Off"
        cmake.definitions["BUILD_shared"] = self.options.shared
        cmake.definitions["BUILD_tests"] = "Off"
        cmake.definitions["BUILD_tools"] = "Off"

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
        self.cpp_info.name = "EXPAT"
        if self.settings.os == "Windows" and self.settings.build_type == "Debug":
            self.cpp_info.libs = ["libexpatd"]
        else:
            self.cpp_info.libs = ["libexpat"]
        if not self.options.shared:
            self.cpp_info.defines = ["XML_STATIC"]
