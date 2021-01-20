import os
from conans import ConanFile, CMake
from conans.errors import ConanInvalidConfiguration


required_conan_version = ">=1.32.0"

class FoobarConan(ConanFile):
    name = "foobar"
    version = "0.1.0"
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    homepage = "http://pudim.com.br/"
    description = "Dummy recipe - DO NOT MERGE"
    topics = ("alea", "jacta", "est")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    exports_sources = "src/*"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Window only")

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="src")
        cmake.build()

    def package(self):
        self.copy("*.h", dst="include", src="src")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.dylib*", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        os.mkdir(os.path.join(self.package_folder, "licenses"))
        with open(os.path.join(self.package_folder, "licenses", "LICENSE"), "w") as fd:
            fd.write("Fake")


    def package_info(self):
        self.cpp_info.libs = ["foobar"]
