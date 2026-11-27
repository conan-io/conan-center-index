from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=2.4"


class GnuplotConan(ConanFile):
    name = "gnuplot"
    description = "Portable command-line driven graphing utility"
    license = "gnuplot"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.gnuplot.info"
    topics = ("plotting", "graphs", "visualization")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_gd": [True, False],
        "with_cairo": [True, False],
    }
    default_options = {
        "with_gd": True,
        "with_cairo": True,
    }
    languages = "C"

    def configure(self):
        if self.options.with_gd:
            self.options["libgd"].with_png = True
            self.options["libgd"].with_jpeg = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def requirements(self):
        if self.options.with_gd:
            self.requires("libgd/2.3.3")
        if self.options.with_cairo:
            self.requires("cairo/1.18.4")
            self.requires("pango/1.58.2")
            self.requires("glib/2.90.1")
            self.requires("libwebp/1.6.0")

    def validate(self):
        # INFO: upstream autotools build does not support Windows, it ships separate config/mingw and config/msvc makefiles
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} is not supported on Windows.")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # INFO: demo installs nothing and its data file rule races under parallel make in out-of-source builds
        replace_in_file(self, os.path.join(self.source_folder, "Makefile.in"),
                        "SUBDIRS = config m4 term src docs man demo share",
                        "SUBDIRS = config m4 term src docs man share")

    def generate(self):
        if not cross_building(self):
            VirtualRunEnv(self).generate(scope="build")
        def yes_no(v): return "yes" if v else "no"
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--datarootdir=${prefix}/res",
            f"--with-gd={yes_no(self.options.with_gd)}",
            f"--with-cairo={yes_no(self.options.with_cairo)}",
            "--with-readline=builtin",
            "--with-qt=no",
            "--disable-wxwidgets",
            "--without-x",
            "--disable-x11-mbfonts",
            "--without-lua",
            "--without-caca",
            "--without-libcerf",
            "--without-amos",
            "--without-latex",
        ])
        if self.options.with_gd and not self.dependencies["libgd"].options.with_freetype:
            # INFO: libgd without freetype still exports gdImageStringFT as a stub that always fails
            tc.configure_args.append("ac_cv_lib_gd_gdImageStringFT=no")
        tc.generate()
        PkgConfigDeps(self).generate()
        AutotoolsDeps(self).generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "Copyright", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "libexec"))
        rmdir(self, os.path.join(self.package_folder, "res", "man"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]

        # INFO: gnuplot compiles its data paths from the configure prefix, which never matches the package folder
        version = Version(self.version)
        data_dir = os.path.join(self.package_folder, "res", "gnuplot", f"{version.major}.{version.minor}")
        for env_info in (self.buildenv_info, self.runenv_info):
            env_info.define_path("GNUPLOT_PS_DIR", os.path.join(data_dir, "PostScript"))
            env_info.define_path("GNUHELP", os.path.join(data_dir, "gnuplot.gih"))
