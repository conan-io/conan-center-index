from conan import ConanFile

from conan.errors import ConanInvalidConfiguration
from conan.tools.layout import basic_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, get, export_conandata_patches, apply_conandata_patches, rm, copy, load, save
from conan.tools.gnu import AutotoolsToolchain, Autotools, AutotoolsDeps
import os


required_conan_version = ">=1.54.0"


class NasRecipe(ConanFile):
    name = "nas"
    description = "The Network Audio System is a network transparent, client/server audio transport system."
    topics = ("audio", "sound")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.radscan.com/nas.html"
    license = "DocumentRef-wave.h:LicenseRef-MIT-advertising"
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
        basic_layout(self, src_folder="src")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        if self.settings.os not in ("FreeBSD", "Linux"):
            raise ConanInvalidConfiguration("Recipe supports Linux only")
        if self.settings.compiler == "clang":
            # See https://github.com/conan-io/conan-center-index/pull/16267#issuecomment-1469824504
            raise ConanInvalidConfiguration("Recipe cannot be built with clang")

    def requirements(self):
        self.requires("xorg/system")

    def build_requirements(self):
        self.tool_requires("bison/3.7.1")
        self.tool_requires("flex/2.6.4")
        self.tool_requires("imake/1.0.8")
        self.tool_requires("xorg-cf-files/1.0.7")
        self.tool_requires("xorg-makedepend/1.0.6")
        self.tool_requires("xorg-gccmakedep/1.0.3")
        self.tool_requires("gnu-config/cci.20210814")

    def source(self):
        get(self, **self.conan_data["sources"][self.version][0],  strip_root=True)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def generate(self):
        autotools = AutotoolsToolchain(self)
        autotools.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        buildenv = VirtualBuildEnv(self)
        buildenv.generate()

    @property
    def _imake_irulesrc(self):
        return self.conf.get("user.xorg-cf-files:config-path")

    @property
    def _imake_defines(self):
        return "-DUsrLibDir={}".format(os.path.join(self.package_folder, "lib"))

    @property
    def _imake_make_args(self):
        return ["IRULESRC={}".format(self._imake_irulesrc), "IMAKE_DEFINES={}".format(self._imake_defines)]

    def build(self):
        apply_conandata_patches(self)

        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                config_folder = os.path.join(self.source_folder, "config")
                copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=config_folder)

        with chdir(self, self.source_folder):
            self.run("imake -DUseInstalled -I{} {}".format(self._imake_irulesrc, self._imake_defines), env="conanbuild")
            autotools = Autotools(self)
            # j1 avoids some errors while trying to run this target
            autotools.make(target="World", args=["-j1"] + self._imake_make_args)

    def _extract_license(self):
        header = "Copyright 1995"
        footer = "Translation:  You can do whatever you want with this software!"
        nas_audio = load(self, os.path.join(self.source_folder, "README"))
        begin = nas_audio.find(header)
        end = nas_audio.find(footer, begin)
        return nas_audio[begin:end]

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())

        tmp_install = os.path.join(self.build_folder, "prefix")
        self.output.warning(tmp_install)
        install_args = [
                        "DESTDIR={}".format(tmp_install),
                        "INCDIR=/include",
                        "ETCDIR=/etc",
                        "USRLIBDIR=/lib",
                        "BINDIR=/bin",
                    ] + self._imake_make_args
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            # j1 avoids some errors while trying to install
            autotools.install(args=["-j1"] + install_args)

        copy(self, "*", src=os.path.join(tmp_install, "bin"), dst=os.path.join(self.package_folder, "bin"))
        copy(self, "*.h", src=os.path.join(tmp_install, "include"), dst=os.path.join(self.package_folder, "include", "audio"))
        copy(self, "*", src=os.path.join(tmp_install, "lib"), dst=os.path.join(self.package_folder, "lib"))

        # Both are present in the final build and there does not seem to be an obvious way to tell the build system
        # to only generate one of them, so remove the unwanted one
        if self.options.shared:
            rm(self, "*.a", os.path.join(self.package_folder, "lib"))
        else:
            rm(self, "*.so*", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["audio"]
        self.cpp_info.requires = ["xorg::xau"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.path.append(bin_path)
