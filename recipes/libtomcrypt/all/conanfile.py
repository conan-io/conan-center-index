from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, chdir, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import VCVars, is_msvc
import os


class LibtomcryptConan(ConanFile):
    name = "libtomcrypt"
    description = "A comprehensive, modular and portable cryptographic toolkit."
    license = "WTFPL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.libtom.net/LibTomCrypt/"
    topics = ("cryptography", "encryption", "security")
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        # Pure C library
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.options.shared:
            raise ConanInvalidConfiguration("Shared build is not supported by upstream makefiles.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            VCVars(self).generate()

    def build(self):
        if is_msvc(self):
            cmd = "nmake /f makefile.msvc CC=cl CFLAGS= EXTRALIBS= tomcrypt.lib"
        else:
            cmd = "make -f makefile.unix CFLAGS= EXTRALIBS= libtomcrypt.a"
        with chdir(self, self.source_folder):
            self.run(cmd, env="conanbuild")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "tomcrypt*.h", src=os.path.join(self.source_folder, "src", "headers"),
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.a", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.lib", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["tomcrypt"]
