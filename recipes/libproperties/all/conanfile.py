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


    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        source_dir="libproperties-{}".format(self.version)
        os.rename(source_dir, self._source_subfolder)
        tools.replace_in_file(source_dir, 
            "project(libproperties VERSION ${LIBPROPERTIES_VERSION} LANGUAGES C)",
            '''
            project(libproperties VERSION ${LIBPROPERTIES_VERSION} LANGUAGES C)
            include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
            conan_basic_setup()
            ''')

    # def source(self):
    #     self.run("git clone https://github.com/tinyhubs/libproperties.git")
    #     # This small hack might be useful to guarantee proper /MT /MD linkage
    #     # in MSVC if the packaged project doesn't have variables to set it
    #     # properly
    #     tools.replace_in_file("libproperties/CMakeLists.txt", 
    #         "project(libproperties VERSION ${LIBPROPERTIES_VERSION} LANGUAGES C)",
    #         '''
    #         project(libproperties VERSION ${LIBPROPERTIES_VERSION} LANGUAGES C)
    #         include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    #         conan_basic_setup()
    #         ''')

    def build(self):
        cmake = CMake(self)
        #cmake.configure(source_folder="libproperties")
        cmake.build()

        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("properties.h", dst="include", src="libproperties")
        self.copy("*properties.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["properties"]
