from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=2.4.0"


class LibmetalinkConan(ConanFile):
    name = "libmetalink"
    description = (
        "Libmetalink is a library to read Metalink XML download description format. "
        "It supports both Metalink version 3 and Metalink version 4 (RFC 5854)."
    )
    license = "MIT"
    topics = ("metalink", "xml")
    homepage = "https://launchpad.net/libmetalink"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "xml_backend": ["expat", "libxml2"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "xml_backend": "expat",
    }
    languages = ["C"]
    implements = ["auto_shared_fpic"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.xml_backend == "expat":
            self.requires("expat/[>=2.6.2 <3]")
        elif self.options.xml_backend == "libxml2":
            self.requires("libxml2/[>=2.12.5 <3]")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} does not support Visual Studio yet")

    def build_requirements(self):
        self.tool_requires("gnu-config/cci.20210814")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/[>=2.2 <3]")
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Support more configurations
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=self.source_folder)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            f"--with-libexpat={yes_no(self.options.xml_backend == 'expat')}",
            f"--with-libxml2={yes_no(self.options.xml_backend == 'libxml2')}",
            "ac_cv_func_malloc_0_nonnull=yes",
        ])
        tc.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libmetalink")
        self.cpp_info.libs = ["metalink"]
