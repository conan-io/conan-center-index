from conans import ConanFile, CMake, tools
import os

class Tinyxml2Conan(ConanFile):
    name = "tinyxml2"
    license = "Zlib"
    homepage = "https://github.com/leethomason/tinyxml2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "TinyXML2 is a simple, small, efficient, C++ XML parser that can be easily integrated into other programs."
    topics = ("xml", "xml-parsel", "tiny-xml")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    source_dir = "tinyxml2"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd        

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)
    
    def _patch_sources(self):
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "project(tinyxml2)", '''project(tinyxml2)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')
    
    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.definitions["BUILD_TESTING"] = False
        cmake.definitions["BUILD_STATIC_LIBS"] = not self.options.shared

        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))
        
        # package the license file
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)


    def package_info(self):
        if not self.settings.build_type == "Debug":
            self.cpp_info.libs = ["tinyxml2"]
        else:
            self.cpp_info.libs = ["tinyxml2d"]
