from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeToolchain
import os

required_conan_version = ">=1.55.0"


class CalcephConan(ConanFile):
    name = "calceph"
    description = "C Library designed to access the binary planetary ephemeris " \
                  "files, such INPOPxx, JPL DExxx and SPICE ephemeris files."
    license = ["CECILL-C", "CECILL-B", "CECILL-2.1"]
    topics = ("ephemeris", "astronomy", "space", "planet")
    homepage = "https://www.imcce.fr/inpop/calceph"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "threadsafe": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "threadsafe": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if is_msvc(self):
            del self.options.threadsafe

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support shared builds with Visual Studio yet")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self):
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            tc = AutotoolsToolchain(self)
            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.extend([
                f"--enable-thread={yes_no(self.options.threadsafe)}",
                "--disable-fortran",
                "--disable-python",
                "--disable-python-package-system",
                "--disable-python-package-user",
                "--disable-mex-octave",
            ])
            tc.generate()

    @property
    def _nmake_args(self):
        return " ".join([
            f"DESTDIR=\"{self.package_folder}\"",
            "ENABLEF2003=0",
            "ENABLEF77=0",
        ])

    def build(self):
        if is_msvc(self):
            replace_in_file(
                self, os.path.join(self.source_folder, "Makefile.vc"),
                "CFLAGS = /O2 /GR- /MD /nologo /EHs",
                "CFLAGS = /nologo /EHs",
            )
            with chdir(self, self.source_folder):
                self.run(f"nmake -f Makefile.vc {self._nmake_args}")
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            with chdir(self, self.source_folder):
                self.run(f"nmake -f Makefile.vc install {self._nmake_args}")
            rmdir(self, os.path.join(self.package_folder, "doc"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "share"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)
        rmdir(self, os.path.join(self.package_folder, "libexec"))

    def package_info(self):
        prefix = "lib" if is_msvc(self) else ""
        self.cpp_info.libs = [f"{prefix}calceph"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            if self.options.threadsafe:
                self.cpp_info.system_libs.append("pthread")

        # TODO: to remove in conan v2
        if not is_msvc(self):
            self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
