from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import AutotoolsToolchain, Autotools, PkgConfigDeps
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.files import get, rmdir, copy, apply_conandata_patches, export_conandata_patches
from conan.tools.env import VirtualBuildEnv
from conan.tools.apple import is_apple_os
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.57.0"


class XorgCfFilesConan(ConanFile):
    name = "xorg-cf-files"
    # package_type = "build-scripts" # see https://github.com/conan-io/conan/issues/13431
    description = "Imake configuration files & templates"
    topics = ("imake", "xorg", "template", "configuration", "obsolete")
    license = "MIT"
    homepage = "https://gitlab.freedesktop.org/xorg/util/cf"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("xorg-macros/1.19.3")
        self.requires("xorg-proto/2022.2")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.arch
        del self.info.settings.build_type
        # self.info.settings.os  # FIXME: can be removed once c3i is able to test multiple os'es from one common package

    def validate(self):
        if is_apple_os(self):
            raise ConanInvalidConfiguration(f"{self.ref} does not support Apple operating systems.")
        if self.settings.compiler == "clang":
            # See https://github.com/conan-io/conan-center-index/pull/16267#issuecomment-1469824504
            raise ConanInvalidConfiguration("Recipe cannot be built with clang")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.0.3")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.build_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        env = tc.environment()
        if is_msvc(self):
            compile_wrapper = unix_path(self, self.conf.get('user.automake:compile-wrapper'))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("CPP", f"{compile_wrapper} cl -E")
        tc.generate(env)

        deps = PkgConfigDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        x11_config_files = os.path.join(self.package_folder, "lib", "X11", "config")
        self.conf_info.define("user.xorg-cf-files:config-path", x11_config_files)

        self.user_info.CONFIG_PATH = x11_config_files.replace("\\", "/")
