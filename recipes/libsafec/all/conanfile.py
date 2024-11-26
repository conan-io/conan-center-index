import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration, ConanException
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LibSafeCConan(ConanFile):
    name = "libsafec"
    description = ("This library implements the secure C11 Annex K functions"
                   " on top of most libc implementations, which are missing from them.")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rurban/safeclib"
    topics = ("safec", "libc", "bounds-checking", "pre-built")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "strmax": ["ANY"],
        "memmax": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "strmax": 4096,
        "memmax": 268435456,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _supported_compiler(self):
        compiler = self.settings.compiler
        version = Version(self.settings.compiler.version)
        if is_msvc(self):
            return False
        if compiler == "gcc" and version < "5":
            return False
        return True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_apple_os(self) and self.settings.arch == "armv8":
            raise ConanInvalidConfiguration(
                f"This platform is not yet supported by {self.ref} (os=Macos arch=armv8)"
            )
        if not self._supported_compiler:
            raise ConanInvalidConfiguration(
                f"{self.ref} doesn't support {self.settings.compiler}-{self.settings.compiler.version}"
            )

        if not str(self.info.options.strmax).isdigit():
            raise ConanException(f"{self.ref} option 'strmax' must be a valid integer number.")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args += [
            f"--enable-debug={yes_no(self.settings.build_type == 'Debug')}",
            "--disable-doc",
            "--disable-Werror",
            f"--enable-strmax={self.options.strmax}",
            f"--enable-memmax={self.options.memmax}",
        ]
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libsafec")

        if Version(self.version) >= "3.7.0":
            self.cpp_info.includedirs.append(os.path.join("include", "safeclib"))
            self.cpp_info.libs = ["safec"]
        else:
            self.cpp_info.includedirs.append(os.path.join("include", "libsafec"))
            self.cpp_info.libs = [f"safec-{self.version}"]

        bin_dir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_dir)
