import os
from conans import ConanFile, CMake, tools


class SvgwriteConan(ConanFile):
    name = "svgwrite"
    version = "0.1"

    license = "Boost Software License"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.com/dvd0101/svgwrite"
    description = "SVGWrite - a streamign svg library"
    topics = ("c++", "svg")

    requires = "span-lite/0.7.0", "fmt/6.1.2"

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake_paths", "cmake_find_package"

    def configure(self):
        tools.check_min_cppstd(self, "17")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        srcdir = [x for x in os.listdir(".") if x.startswith("svgwrite")][0]
        os.rename(srcdir, "svgwrite")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="svgwrite")
        cmake.build()

    def package(self):
        self.copy("*.hpp", dst="include", src="svgwrite/include")
        self.copy("*hello.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("LICENSE", dst="licenses", src="svgwrite")

    def package_info(self):
        self.cpp_info.libs = ["svgwrite"]
