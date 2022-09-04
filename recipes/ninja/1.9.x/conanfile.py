import os
import sys
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class NinjaConan(ConanFile):
    name = "ninja"
    description = "Ninja is a small build system with a focus on speed"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ninja-build/ninja"
    settings = "os", "arch", "compiler", "build_type"
    topics = ("conan", "ninja", "build")

    _source_subfolder = "source_subfolder"

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if hasattr(self, 'settings_build') and tools.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building not implemented")

    def _build_vs(self):
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self.settings, filter_known_paths=False):
                self.run("%s configure.py --bootstrap" % sys.executable)

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            cxx = os.environ.get("CXX", "g++")
            if self.settings.os == "Linux":
                if self.settings.arch == "x86":
                    cxx += " -m32"
                elif self.settings.arch == "x86_64":
                    cxx += " -m64"
            env_build = AutoToolsBuildEnvironment(self)
            env_build_vars = env_build.vars
            env_build_vars.update({'CXX': cxx})
            with tools.environment_append(env_build_vars):
                self.run("%s configure.py --bootstrap" % sys.executable)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("ninja-%s" % self.version, self._source_subfolder)

    def build(self):
        if self.settings.os == "Windows":
            self._build_vs()
        else:
            self._build_configure()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses",
                  src=self._source_subfolder)
        self.copy(pattern="ninja*", dst="bin", src=self._source_subfolder)
        pdb = os.path.join(self.package_folder, "bin", "ninja.pdb")
        if os.path.isfile(pdb):
            os.unlink(pdb)

    def package_info(self):
        self.cpp_info.includedirs = []
        # ensure ninja is executable
        if self.settings.os in ["Linux", "Macos"]:
            name = os.path.join(self.package_folder, "bin", "ninja")
            os.chmod(name, os.stat(name).st_mode | 0o111)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.CONAN_CMAKE_GENERATOR = "Ninja"
