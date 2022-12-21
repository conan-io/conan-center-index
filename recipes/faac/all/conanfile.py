from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class FaacConan(ConanFile):
    name = "faac"
    description = "Freeware Advanced Audio Coder"
    topics = ("audio", "mp4", "encoder", "aac", "m4a", "faac")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/faac"
    license = "LGPL-2.0-only"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_mp4": [True, False],
        "drm": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_mp4": False,
        "drm": False,
    }

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _has_mp4_option(self):
        return Version(self.version) < "1.29.1"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_mp4_option:
            del self.options.with_mp4

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # FIXME: libfaac depends on kissfft. Try to unvendor this dependency
        pass

    def validate(self):
        if is_msvc(self):
            # FIXME: add msvc support since there are MSBuild files upstream
            raise ConanInvalidConfiguration("libfaac conan-center recipe doesn't support building with Visual Studio yet")
        if self.options.get_safe("with_mp4"):
            # TODO: as mpv4v2 as a conan package
            raise ConanInvalidConfiguration("building with mp4v2 is not supported currently")

    def build_requirements(self):
        self.tool_requires("libtool/2.4.7")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.append(f"--enable-drm={yes_no(self.options.drm)}")
        if self._has_mp4_option:
            tc.configure_args.append(f"--with-mp4v2={yes_no(self.options.with_mp4)}")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.autoreconf()
        if self._is_mingw and self.options.shared:
            replace_in_file(self, os.path.join(self.build_folder, "libfaac", "Makefile"),
                            "\nlibfaac_la_LIBADD = ",
                            "\nlibfaac_la_LIBADD = -no-undefined ")
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["faac"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")

        # TODO: to replace in conan v2
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
