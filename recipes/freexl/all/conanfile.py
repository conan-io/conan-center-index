from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeDeps, NMakeToolchain
from conan.tools.scm import Version
import os

required_conan_version = ">=1.55.0"


class FreexlConan(ConanFile):
    name = "freexl"
    description = "FreeXL is an open source library to extract valid data " \
                  "from within an Excel (.xls) spreadsheet."
    license = ["MPL-1.0", "GPL-2.0-only", "LGPL-2.1-only"]
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gaia-gis.it/fossil/freexl/index"
    topics = ("excel", "xls")
    package_type = "library"
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

    def export_sources(self):
        export_conandata_patches(self)

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
        self.requires("libiconv/1.17")
        if Version(self.version) >= "2.0.0":
            self.requires("expat/[>=2.6.2 <3]")
            self.requires("minizip/1.2.13")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("gnu-config/cci.20210814")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
            deps = NMakeDeps(self)
            deps.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")
            tc = AutotoolsToolchain(self)
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            args = "freexl_i.lib FREEXL_EXPORT=-DDLL_EXPORT" if self.options.shared else "freexl.lib"
            with chdir(self, self.source_folder):
                self.run(f"nmake -f makefile.vc {args}")
        else:
            for gnu_config in [
                self.conf.get("user.gnu-config:config_guess", check_type=str),
                self.conf.get("user.gnu-config:config_sub", check_type=str),
            ]:
                if gnu_config:
                    copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=self.source_folder)
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self, "freexl.h", src=os.path.join(self.source_folder, "headers"), dst=os.path.join(self.package_folder, "include"))
            copy(self, "*.lib", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "freexl")
        suffix = "_i" if is_msvc(self) and self.options.shared else ""
        self.cpp_info.libs = [f"freexl{suffix}"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("m")
