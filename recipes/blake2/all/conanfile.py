import os
import stat
import shutil
from conans import ConanFile, tools, AutoToolsBuildEnvironment

class blake2Conan(ConanFile):
    name = "blake2"
    version = "997fa5b" #BLAKE2 doesn't have versions so we use the commit hash instead
    license = "	CC0-1.0, OpenSSL, APSL 2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/BLAKE2/BLAKE2"
    description = ("BLAKE2 is a cryptographic hash function faster than MD5, \
                    SHA-1, SHA-2, and SHA-3, yet is at least as secure as the latest standard SHA-3")
    settings = "os", "arch", "compiler", "build_type"
    topics = ("conan", "blake2", "hash")
    exports_sources = ["makefile"]
    options = {"fPIC": [True, False], "use_sse": [True, False]}
    default_options = {"fPIC": True, "use_sse": True}
    _source_subfolder = "source_subfolder"
    _env_build = None
    _env_vars = None


    def _configure_envbuilds(self):
        if not self._env_build:
            self._env_build = AutoToolsBuildEnvironment(self)
            self._env_vars = self._env_build.vars
            if self.settings.arch == "x86_64":
                if self.options.use_sse:
                    self._env_vars['USE_SSE'] = "True"
                else:
                    self._env_vars['USE_REF'] = "True"
            elif "arm" in self.settings.arch:
                self._env_vars['USE_NEON'] = "True"
            self._env_vars['DESTDIR'] = self.package_folder
        return self._env_build

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch != "x86_64":
            del self.options.use_sse

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        #Get te extracted folder name. Its BLAKE2-githubCommit
        listdir = os.listdir()
        extracted_dir = [i for i in listdir if "BLAKE2-" in i][0]
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        #Move makefile into _source_subfolder.
        shutil.move(src=os.path.join(self.source_folder, "makefile"), dst=os.path.join(self.source_folder,self._source_subfolder, "makefile"))
        with tools.chdir(self._source_subfolder):
            env_build = self._configure_envbuilds()
            env_build.make(vars=self._env_vars)

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with tools.chdir(self._source_subfolder):
            env_build = self._configure_envbuilds()
            env_build.install(vars=self._env_vars)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include",os.path.join("include","blake2")]
