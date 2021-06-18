from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class XegeConan(ConanFile):
    name = "xege"
    version = "20.08"
    license = "LGPLv2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://xege.org/"
    description = "Easy Graphics Engine, a lite graphics library in Windows"
    topics = ("ege", "graphics", "gui")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake"

    def configure(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration(
                "This library is only compatible for Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, "source_subfolder")
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly
#         tools.replace_in_file("hello/CMakeLists.txt", "PROJECT(HelloWorld)",
#                               '''PROJECT(HelloWorld)
# include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
# conan_basic_setup()''')

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="source_subfolder")
        cmake.build()

        # Explicit way:
        # self.run('cmake %s/hello %s'
        #          % (self.source_folder, cmake.command_line))
        # self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src="source_subfolder/src")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("LICENSE", dst="licenses", src="source_subfolder")

    def package_info(self):
        if self.settings.arch == "x86_64":
            self.cpp_info.libs = ["graphics64"]
        else:
            self.cpp_info.libs = ["graphics"]
        if self.settings.compiler == "gcc":
            self.cpp_info.system_libs = [
                "gdiplus",
                "uuid",
                "msimg32",
                "gdi32",
                "imm32",
                "ole32",
                "oleaut32",
                "winmm"
            ]
