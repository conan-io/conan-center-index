from conan import ConanFile
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy, rename, rmdir, rm, export_conandata_patches, apply_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.env import VirtualBuildEnv
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc, unix_path
import os

required_conan_version = ">=1.52.0"


class LibexifConan(ConanFile):
    name = "libexif"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libexif.github.io/"
    license = "LGPL-2.1"
    description = "libexif is a library for parsing, editing, and saving EXIF data."
    topics = ("exif", "metadata", "parse", "edit")
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

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def layout(self):
        basic_layout(self, src_folder="src")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        self.tool_requires("gettext/0.21")
        self.tool_requires("libtool/2.4.6")
        if self._settings_build.os == "Windows":
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
                self.tool_requires("msys2/cci.latest")
            self.win_bash = True

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--disable-docs",
            "--disable-nls",
            "--disable-rpath",
        ])
        if (self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) >= "12") or \
                (self.settings.compiler == "msvc" and Version(self.settings.compiler.version) >= "180"):
            tc.extra_cflags.append("-FS")

        # env vars
        env = tc.environment()
        if is_msvc(self):
            compile_wrapper = unix_path(self, self._user_info_build["automake"].compile).replace("\\", "/")
            ar_wrapper = unix_path(self, self._user_info_build["automake"].ar_lib).replace("\\", "/")
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("AR", f"{ar_wrapper} lib")
            env.define("LD", f"{compile_wrapper} link -nologo")

        tc.generate(env)

        env = VirtualBuildEnv(self)
        env.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
        if is_msvc(self) and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "exif.dll.lib"),
                         os.path.join(self.package_folder, "lib", "exif.lib"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["exif"]
        self.cpp_info.names["pkg_config"] = "libexif"
        self.cpp_info.set_property("pkg_config_name", "libexif")
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["m"]
