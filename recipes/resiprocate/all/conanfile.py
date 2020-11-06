import tempfile
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class ResiprocateConan(ConanFile):
    name = "resiprocate"
    description = "The project is dedicated to maintaining a complete, correct, and commercially usable implementation of SIP and a few related protocols. "
    topics = ("conan", "resiprocate", "sip")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.resiprocate.org"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    license = "VSL-1.0"
    install_dir = tempfile.mkdtemp(suffix=name)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def build(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = True
        env_build.cxx_flags.append("-w")
        with tools.environment_append(env_build.vars):
            configure_args = ['--prefix=%s' % self.install_dir]
            with tools.chdir("%s-%s" % (self.name, self.version)):
                env_build.configure(args=configure_args)
                env_build.make(args=["clean"])
                env_build.make(args=["install"])

    def package(self):
        self.copy(pattern="*", dst="include/repro", src=os.path.join(self.name, "repro"))
        self.copy(pattern="*", dst="include/resip", src=os.path.join(self.name, "resip"))
        self.copy(pattern="*", dst="include/rutil", src=os.path.join(self.name, "rutil"))
        self.copy(pattern="*.a", dst="lib", src=os.path.join(self.install_dir, "lib"))
        self.copy(pattern="*.la", dst="lib", src=os.path.join(self.install_dir, "lib"))
        self.copy(pattern="*.so", dst="lib", src=os.path.join(self.install_dir, "lib"))
        self.copy(pattern="*.lib", dst="lib", src=os.path.join(self.install_dir, "lib"))

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.libs = ["resip", "rutil", "dum", "resipares"]
