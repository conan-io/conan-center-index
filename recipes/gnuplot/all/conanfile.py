from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os

required_conan_version = ">=1.50.0"


class GnuplotConan(ConanFile):
    name = "gnuplot"
    description = (
        "A famous scientific plotting package, features include 2D and 3D plotting, "
        "a huge number of output formats, interactive input or script-driven options, "
        "and a large set of scripted examples."
    )
    license = "gnuplot"
    topics = ("plotting")
    homepage = "http://www.gnuplot.info"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")
        self.requires("zlib/1.2.13")

    def package_id(self):
        del self.info.settings.compiler

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--without-libcerf",
            "--without-latex",
            "--without-texdir",
            "--without-ggi",
            "--without-readline",
            "--without-gd",
            "--without-lua",
            "--without-caca",
            "--without-cwdrc",
            "--without-wx",
            "--without-cairo",
            "--without-qt",
        ])
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

        if is_msvc(self):
            env = Environment()
            compile_wrapper = unix_path(self, os.path.join(self.source_folder, "compile"))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_gnuplot_msvc")

    def _patch_sources(self):
        replace_in_file(
            self,
            os.path.join(self.source_folder, "configure"),
            "-lz",
            f"-l{self.dependencies['zlib'].cpp_info.libs[0]}",
        )

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "Copyright", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
        rmdir(self, os.path.join(self.package_folder, "libexec"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
