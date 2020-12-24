from conans import ConanFile, CMake, tools
import os


class LibpropertiesConan(ConanFile):
    name = "libproperties"
    license = "Apache-2.0"
    homepage = "https://github.com/tinyhubs/libproperties"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libproperties is a library to parse the Java .properties files. It was writen in pure C. And fully compatible with the Java .properties file format."
    topics = ("properties", "java", "pure-c")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False],}
    default_options = {"shared": False, "fPIC": True,}
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "sources"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        source_package_tag = "{}-{}".format(self.name, self.version)
        tools.get(**self.conan_data["sources"][source_package_tag])
        tools.replace_in_file(source_package_tag,
            "project(libproperties VERSION ${LIBPROPERTIES_VERSION} LANGUAGES C)",
            '''
            project(libproperties VERSION ${LIBPROPERTIES_VERSION} LANGUAGES C)
            include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
            conan_basic_setup()
            ''')

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["properties"]
