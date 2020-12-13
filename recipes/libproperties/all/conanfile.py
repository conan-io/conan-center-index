from conans import ConanFile, CMake, tools


class LibpropertiesConan(ConanFile):
    name = "libproperties"
    license = "Apache-2.0 License"
    author = "libbylg@126.com"
    url = "https://github.com/tinyhubs/libproperties"
    description = "libproperties is a library to parse the Java .properties files. It was writen in pure C. And fullly compatible with the Java .properties file format."
    topics = ("properties", "java", "pure-c")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"

    def source(self):
        self.run("git clone https://github.com/tinyhubs/libproperties.git")
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
        tools.replace_in_file("libproperties/CMakeLists.txt", "PROJECT(libproperties)",
                              '''PROJECT(libproperties)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="libproperties")
        cmake.build()

        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("properties.h", dst="include", src="libproperties")
        self.copy("*properties.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["libproperties"]
