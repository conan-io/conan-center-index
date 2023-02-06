from conan import ConanFile

from conan.tools.layout import basic_layout
from conan.tools.files import get, download, replace_in_file, rm, copy
from conan.tools.gnu import AutotoolsToolchain, Autotools, AutotoolsDeps
from conans.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.33.0"


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

    def layout(self):
        basic_layout(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def validate(self):
        if self.settings.os not in ("FreeBSD", "Linux"):
            raise ConanInvalidConfiguration("Recipe supports Linux only")

    def requirements(self):
        self.requires("xorg/system")

    def build_requirements(self):
        self.tool_requires("bison/3.7.1")
        self.tool_requires("flex/2.6.4")
        self.tool_requires("imake/1.0.8")
        self.tool_requires("xorg-cf-files/1.0.7")
        self.tool_requires("xorg-makedepend/1.0.6")
        self.tool_requires("xorg-gccmakedep/1.0.3")

    def source(self):
        get(self, **self.conan_data["sources"][self.version][0],  strip_root=True)
        download(filename="LICENSE", **self.conan_data["sources"][self.version][1])

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def generate(self):
        autotools = AutotoolsToolchain(self)
        # autotools.libs = []
        autotools.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    @property
    def _imake_irulesrc(self):
        return self._user_info_build["xorg-cf-files"].CONFIG_PATH

    @property
    def _imake_defines(self):
        return "-DUsrLibDir={}".format(os.path.join(self.package_folder, "lib"))

    @property
    def _imake_make_args(self):
        return ["IRULESRC={}".format(self._imake_irulesrc), "IMAKE_DEFINES={}".format(self._imake_defines)]

    def build(self):
        replace_in_file(os.path.join(self.source_folder, "server", "dia", "main.c"),
                              "\nFILE *yyin", "\nextern FILE *yyin")
        self.run("imake -DUseInstalled -I{} {}".format(self._imake_irulesrc, self._imake_defines), run_environment=True)
        autotools = Autotools(self)
        autotools.make(target="World", args=["-j1"] + self._imake_make_args)

    def package(self):
        copy(self, "LICENSE", dst="licenses")

        autotools = Autotools(self)
        tmp_install = os.path.join(self.build_folder, "prefix")
        install_args = [
                           "DESTDIR={}".format(tmp_install),
                           "INCDIR=/include",
                           "ETCDIR=/etc",
                           "USRLIBDIR=/lib",
                           "BINDIR=/bin",
                       ] + self._imake_make_args
        autotools.install(args=["-j1"] + install_args)

        copy(self, "*", src=os.path.join(tmp_install, "bin"), dst="bin")
        copy(self, "*", src=os.path.join(tmp_install, "include"), dst=os.path.join("include", "audio"))
        copy(self, "*", src=os.path.join(tmp_install, "lib"), dst="lib")

        if self.options.shared:
            rm(self, os.path.join(self.package_folder, "lib"), "*.a")
        else:
            rm(self, os.path.join(self.package_folder, "lib"), "*.so*")

    def package_info(self):
        self.cpp_info.libs = ["audio"]
        self.cpp_info.requires = ["xorg::xau"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.path.append(bin_path)
