from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.54.0"


class LibGphoto2(ConanFile):
    name = "libgphoto2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The libgphoto2 camera access and control library."
    homepage = "http://www.gphoto.org/"
    license = "LGPL-2.1"
    topics = ("gphoto2", "libgphoto2", "libgphoto", "photo")
    package_type = "shared-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_libusb": [True, False],
        "with_libcurl": [True, False],
        "with_libxml2": [True, False],
        "with_libexif": [True, False],
        "with_libjpeg": [True, False],
    }
    default_options = {
        "with_libusb": True,
        "with_libcurl": True,
        "with_libxml2": True,
        "with_libexif": True,
        "with_libjpeg": True,
    }

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
        self.requires("libtool/2.4.7")
        if self.options.with_libusb:
            self.requires("libusb/1.0.26")
        if self.options.with_libcurl:
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.with_libxml2:
            self.requires("libxml2/2.12.3")
        if self.options.with_libexif:
            self.requires("libexif/0.6.24")
        if self.options.with_libjpeg:
            self.requires("libjpeg/9e")

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("Visual Studio not supported yet")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.1.0")
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
        auto_no = lambda v: "auto" if v else "no"
        tc.configure_args.extend([
            f"--with-libcurl={auto_no(self.options.with_libcurl)}",
            f"--with-libexif={auto_no(self.options.with_libexif)}",
            f"--with-libxml-2.0={auto_no(self.options.with_libxml2)}",
            "--disable-nls",
            "--datadir=${prefix}/res",
            "udevscriptdir=${prefix}/res",
            "utilsdir=${prefix}/bin",
        ])
        if not self.options.with_libjpeg:
            tc.configure_args.append("--without-jpeg")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()
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
        rm(self, "*.la", os.path.join(self.package_folder, "lib"), recursive=True)
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libgphoto2")
        self.cpp_info.libs = ["gphoto2", "gphoto2_port"]
        self.cpp_info.includedirs.append(os.path.join("include", "gphoto2"))
        self.cpp_info.resdirs = ["res"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["dl"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["m"]
