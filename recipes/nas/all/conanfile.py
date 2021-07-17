from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class NasRecipe(ConanFile):
    name = "nas"
    description = "The Network Audio System is a network transparent, client/server audio transport system."
    topics = ("audio", "sound")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.radscan.com/nas.html"
    license = "Unlicense"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = {'shared': False}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Recipe supports Linux only")

    def build_requirements(self):
        self.build_requires("bison/3.7.1")
        self.build_requires("flex/2.6.4")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0], strip_root=True, destination=self._source_subfolder)
        tools.download(filename="LICENSE", **self.conan_data["sources"][self.version][1])

    def build(self):
        with tools.chdir(self._source_subfolder):
            env_build = AutoToolsBuildEnvironment(self)
            self.run("xmkmf")
            env_build.make(target="World")

    def package(self):
        self.copy("LICENSE", dst="licenses")
        
        tmp_install = os.path.join(self.build_folder, "tmp-install")
        with tools.chdir(self._source_subfolder):
            env_build = AutoToolsBuildEnvironment(self)
            env_build_vars = env_build.vars
            env_build_vars['DESTDIR'] = tmp_install  #self.package_folder
            env_build.install(vars=env_build_vars)

        self.copy("*", src=os.path.join(tmp_install, "usr"), dst=self.package_folder)

        shutil.rmtree(os.path.join(self.package_folder, "lib", "X11"))
        with tools.chdir(os.path.join(self.package_folder, "lib")):
            files = os.listdir()
            for f in files:
                if (self.options.shared and f.endswith(".a")) or (not self.options.shared and not f.endswith(".a")):
                    os.unlink(f)

    def package_info(self):
        self.cpp_info.libs = ["audio"]
        self.cpp_info.system_libs = ["Xau"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.path.append(bin_path)
