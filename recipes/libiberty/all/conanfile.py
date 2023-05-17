from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rename, rmdir
from conan.tools.layout import basic_layout
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.microsoft import is_msvc, unix_path
import os

required_conan_version = ">=1.53.0"


class LibibertyConan(ConanFile):
    name = "libiberty"
    description = "A collection of subroutines used by various GNU programs"
    topics = ("gnu", "gnu-collection")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gcc.gnu.org/onlinedocs/libiberty"
    license = "LGPL-2.1"
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _libiberty_folder(self):
        return os.path.join(self.source_folder, "libiberty")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("libiberty can not be built by Visual Studio.")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        rmdir(self, os.path.join(self.source_folder, "gcc"))
        rmdir(self, os.path.join(self.source_folder, "libstdc++-v3"))

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--enable-install-libiberty")
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure(build_script_folder=self._libiberty_folder)
        autotools.make()

    def package(self):
        copy(self, "COPYING.LIB", src=self._libiberty_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        # TODO: replace by autotools.install() once https://github.com/conan-io/conan/issues/12153 fixed
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
        self._package_xx(32)
        self._package_xx(64)

    def _package_xx(self, arch):
        lib_arch_dir = os.path.join(self.package_folder, f"lib{arch}")
        if os.path.exists(lib_arch_dir):
            libdir = os.path.join(self.package_folder, "lib")
            rmdir(self, libdir)
            rename(self, lib_arch_dir, libdir)

    def package_info(self):
        self.cpp_info.libs = ["iberty"]
