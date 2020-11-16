from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os

class Argon2Conan(ConanFile):
    name = "argon2"
    license = "Apache 2.0", "CC0-1.0"
    homepage = "https://github.com/P-H-C/phc-winner-argon2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Argon2 password hashing library"
    topics = ("argon2", "crypto", "password hashing")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("argon2 recipe currently does not offer Windows support")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("phc-winner-argon2-{0}".format(self.version), "argon2")

    def build(self):
        arch = str(self.settings.arch).replace("_", "-")
        with tools.chdir("argon2"):
            self.run("make OPTTARGET="+arch+" libs")

    def package(self):
        self.copy("*LICENSE", src="", dst="licenses", keep_path=False)
        self.copy("*argon2.h", dst=os.path.join("include", "argon2"), src="", keep_path=False)
        
        if self.options.shared:
            if self.settings.os == "Linux":
                self.run("ln -s libargon2.so.1 libargon2.so")
                self.copy("*argon2.so*", dst="lib", src="", keep_path=False, symlinks=True)
            elif self.settings.os == "Macos":
                self.copy("*.dylib", dst="lib", src="", keep_path=False)
        
        self.copy("*argon2.a", dst="lib", src="", keep_path=False)

    def package_info(self):
        self.cpp_info.includedirs = ['include']
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.libs = ['argon2']        
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ['pthread']
