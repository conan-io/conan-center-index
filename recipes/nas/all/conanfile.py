from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os


class NasRecipe(ConanFile):
    name = "nas"
    description = "The Network Audio System is a network transparent, client/server audio transport system."
    topics = ("audio", "sound")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.radscan.com/nas.html"
    license = "Unlicense"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os not in ("FreeBSD", "Linux"):
            raise ConanInvalidConfiguration("Recipe supports Linux only")

    def requirements(self):
        self.requires("xorg/system")

    def build_requirements(self):
        self.build_requires("bison/3.7.1")
        self.build_requires("flex/2.6.4")
        self.build_requires("imake/1.0.8")
        self.build_requires("xorg-cf-files/1.0.7")
        self.build_requires("xorg-makedepend/1.0.6")
        self.build_requires("xorg-gccmakedep/1.0.3")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][0], destination=self._source_subfolder, strip_root=True)
        tools.download(filename="LICENSE", **self.conan_data["sources"][self.version][1])

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self)
        return autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            env_build = AutoToolsBuildEnvironment(self)
            self.run("imake -DUseInstalled -I{} -DUsrLibDir={}".format(os.path.join(self._user_info_build["xorg-cf-files"].CONFIG_PATH), os.path.join(self.package_folder, "lib")), run_environment=True)
            autotools = self._configure_autotools()
            with tools.environment_append(autotools.vars):
                env_build.make(target="World")

    def package(self):
        self.copy("LICENSE", dst="licenses")

        tmp_install = os.path.join(self.build_folder, "prefix")
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            env_build_vars = autotools.vars
            with tools.environment_append(env_build_vars):
                autotools.install(args=[
                    "DESTDIR={}".format(tmp_install), "INCDIR=/include", "ETCDIR=/etc", "USRLIBDIR=/lib", "BINDIR=/bin"])

        self.copy("*", src=os.path.join(tmp_install, "bin"), dst="bin")
        self.copy("*", src=os.path.join(tmp_install, "include"), dst=os.path.join("include", "audio"))
        self.copy("*", src=os.path.join(tmp_install, "lib"), dst="lib")

        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.a")
        else:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.so*")

    def package_info(self):
        self.cpp_info.libs = ["audio"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.path.append(bin_path)
