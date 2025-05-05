from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.54.0"


class FontconfigConan(ConanFile):
    name = "fontconfig"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Fontconfig is a library for configuring and customizing font access"
    homepage = "https://gitlab.freedesktop.org/fontconfig/fontconfig"
    topics = ("fonts", "freedesktop")
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
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("freetype/2.13.2")
        self.requires("expat/2.6.0")
        if self.settings.os == "Linux":
            self.requires("util-linux-libuuid/2.39.2")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("fontconfig does not support Visual Studio for versions < 2.13.93.")

    def build_requirements(self):
        self.tool_requires("gperf/3.1")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.0.3")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            f"--enable-shared={yes_no(self.options.shared)}",
            f"--enable-static={yes_no(not self.options.shared)}",
            "--disable-docs",
            "--disable-nls",
            "--sysconfdir=${prefix}/bin/etc",
            "--datadir=${prefix}/bin/share",
            "--datarootdir=${prefix}/bin/share",
            "--localstatedir=${prefix}/bin/var",
        ])
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

    def _patch_files(self):
        # fontconfig requires libtool version number, change it for the corresponding freetype one
        replace_in_file(
            self, os.path.join(self.generators_folder, "freetype2.pc"),
            "Version: {}".format(self.dependencies["freetype"].ref.version),
            "Version: {}".format(self.dependencies["freetype"].conf_info.get("user.freetype:libtool_version")),
        )
        # disable fc-cache test to enable cross compilation but also builds with shared libraries on MacOS
        replace_in_file(self,
            os.path.join(self.source_folder, "Makefile.in"),
            "@CROSS_COMPILING_TRUE@RUN_FC_CACHE_TEST = false",
            "RUN_FC_CACHE_TEST=false"
        )

    def build(self):
        self._patch_files()
        autotools = Autotools(self)
        autotools.configure()
        replace_in_file(self, os.path.join(self.build_folder, "Makefile"), "po-conf test", "po-conf")
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
        rm(self, "*.conf", os.path.join(self.package_folder, "bin", "etc", "fonts", "conf.d"))
        rm(self, "*.def", os.path.join(self.package_folder, "lib"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "etc"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Fontconfig")
        self.cpp_info.set_property("cmake_target_name", "Fontconfig::Fontconfig")
        self.cpp_info.set_property("pkg_config_name", "fontconfig")
        self.cpp_info.libs = ["fontconfig"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["m", "pthread"])

        fontconfig_file = os.path.join(self.package_folder, "bin", "etc", "fonts", "fonts.conf")
        self.runenv_info.prepend_path("FONTCONFIG_FILE", fontconfig_file)

        fontconfig_path = os.path.join(self.package_folder, "bin", "etc", "fonts")
        self.runenv_info.prepend_path("FONTCONFIG_PATH", fontconfig_path)

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "Fontconfig"
        self.cpp_info.names["cmake_find_package_multi"] = "Fontconfig"
        self.env_info.FONTCONFIG_FILE = fontconfig_file
        self.env_info.FONTCONFIG_PATH = fontconfig_path
