
import os
import shutil
from conans import ConanFile, tools, AutoToolsBuildEnvironment


class LibOauth(ConanFile):
    name = "liboauth"
    description = "POSIX-C functions implementing the OAuth Core RFC 5849 standard"
    topics = ("conan", "oauth")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/x42/liboauth"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    
    #generators = "cmake"

    _source_subfolder = "source_subfolder"
    
    requires = "openssl/1.0.2t"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.environment_append(autotools.vars):
            with tools.chdir(self._source_subfolder):
                self.run("autoreconf -i")
                self.run("autoconf")
                args = ["--prefix={}".format(self.package_folder)]  # ["--disable-all-programs", "--enable-libmount", "--enable-libblkid"]
                if self.options.shared:
                    args.extend(["--disable-static", "--enable-shared"])
                else:
                    args.extend(["--disable-shared", "--enable-static"])
                self.run("./configure {}".format(" ".join(args)))
                self.run("make")
                self.run("make install")

    def package(self):
        shutil.rmtree(os.path.join(self.package_folder, 'share'), ignore_errors=True)
        shutil.rmtree(os.path.join(self.package_folder, 'lib', 'pkgconfig'), ignore_errors=True)
        if os.path.isfile(os.path.join(self.package_folder, 'lib', 'liboauth.la')):
            os.remove(os.path.join(self.package_folder, 'lib', 'liboauth.la'))

    def package_info(self):
        self.cpp_info.libs = ["oauth"]
        #self.cpp_info.libs = ["m", "curl", "crypto", "oauth"]
