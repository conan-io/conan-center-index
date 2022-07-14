from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.33.0"

class LibisalConan(ConanFile):
    name = "isa-l"
    description = "Intel's Intelligent Storage Acceleration Library"
    license = "BSD-3"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/01org/isa-l"
    topics = ("isa-l", "compression")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC" :True
    }
    build_requires = (
        "libtool/2.4.6",
        "nasm/2.15.05",
    )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.arch not in [ "x86", "x86_64", "armv8" ]:
            raise ConanInvalidConfiguration("CPU Architecture not supported")
        if self.settings.os == "Macos":
            raise ConanInvalidConfiguration("Macos builds not supported")

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_thread
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _posix_build(self):
        self.run("./autogen.sh")
        tools.mkdir("_build")
        with tools.chdir("_build"):
            env_build = AutoToolsBuildEnvironment(self)
            extra_args = list()
            if self.options.shared:
                extra_args.extend(('--enable-static=no',))
            else:
                extra_args.extend(('--enable-shared=no',))
            env_build.configure("../", args=extra_args, build=False, host=False, target=False)
            env_build.make()

    def _windows_build(self):
        self.run("nmake -f Makefile.nmake")

    def build(self):
        with tools.chdir(self._source_subfolder):
            if self.settings.os == "Windows":
                self._windows_build()
            else:
                self._posix_build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*/isa-l.h", dst="include/isa-l", keep_path=False)
        self.copy("*.h", dst="include/isa-l", src="%s/include" % (self._source_subfolder) , keep_path=False)
        if self.options.shared:
            self.copy("*.dll", dst="bin", keep_path=False)
            self.copy("*.so*", dst="lib", keep_path=False, symlinks=True)
            self.copy("*.dylib", dst="lib", keep_path=False)
        else:
            self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
