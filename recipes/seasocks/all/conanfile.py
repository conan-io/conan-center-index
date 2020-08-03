from conans import ConanFile, CMake, tools
import os


class SeasocksConan(ConanFile):
    name = "seasocks"
    description = "Simple, small, C++ embeddable webserver with WebSockets support"
    topics = ("conan", "seasocks", "websockets", "http")
    license = 'BSD 2-clause "Simplified" License'
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mattgodbolt/seasocks"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    exports_sources = "src/main/c/*"

    def requirements(self):
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("seasocks-" + self.version, "seasocks")
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file("seasocks/CMakeLists.txt", "project(Seasocks VERSION " + self.version + ")", 'project(Seasocks VERSION ' + self.version + ''')
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(build_folder="build")
        return cmake

    def build(self):
        cmake = self._config_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src="seasocks")
        cmake = self._config_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["seasocks"]
