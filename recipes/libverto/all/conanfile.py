from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=1.54.0"


class LibVertoConan(ConanFile):
    name = "libverto"
    description = "An async event loop abstraction library."
    homepage = "https://github.com/latchset/libverto"
    topics = ("async", "eventloop")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "pthread": [True, False],
        "with_glib": ["builtin", "external", False],
        "with_libev": ["builtin", "external", False],
        "with_libevent": ["builtin", "external", False],
        "with_tevent": ["external", False],  # tevent cannot be a builtin backend
        "default": ["glib", "libev", "libevent", "tevent"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "pthread": True,
        "with_glib": False,
        "with_libev": False,
        "with_libevent": "builtin",
        "with_tevent": False,
        "default": "libevent",
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _backend_dict(self):
        return {
            "glib": self.options.with_glib,
            "libev": self.options.with_libev,
            "libevent": self.options.with_libevent,
            "tevent": self.options.with_tevent,
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.pthread

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_glib:
            self.requires("glib/2.76.0")
        if self.options.with_libevent:
            self.requires("libevent/2.1.12")
        if self.options.with_libev:
            self.requires("libev/4.33")

    def package_id(self):
        del self.info.options.default

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("libverto does not support Visual Studio")
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared libraries are not supported on Windows")

        if not self._backend_dict[str(self.options.default)]:
            raise ConanInvalidConfiguration(f"Default backend({self.options.default}) must be available")

        count = lambda iterable: sum(1 if it else 0 for it in iterable)
        count_builtins = count(str(opt) == "builtin" for opt in self._backend_dict.values())
        count_externals = count(str(opt) == "external" for opt in self._backend_dict.values())
        if count_builtins > 1:
            raise ConanInvalidConfiguration("Cannot have more then one builtin backend")
        if not self.options.shared:
            if count_externals > 0:
                raise ConanInvalidConfiguration("Cannot have an external backend when building a static libverto")
        if count_builtins > 0 and count_externals > 0:
            raise ConanInvalidConfiguration("Cannot combine builtin and external backends")
        if self.options.with_tevent:
            # FIXME: missing tevent recipe
            raise ConanInvalidConfiguration("tevent is not (yet) available on conan-center")

    def build_requirements(self):
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/1.9.3")
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
        yes_no_builtin = lambda v: {"external": "yes", "False": "no", "builtin": "builtin"}[str(v)]
        tc.configure_args.extend([
            f"--with-pthread={yes_no(self.options.get_safe('pthread'))}",
            f"--with-glib={yes_no_builtin(self.options.with_glib)}",
            f"--with-libev={yes_no_builtin(self.options.with_libev)}",
            f"--with-libevent={yes_no_builtin(self.options.with_libevent)}",
            f"--with-tevent={yes_no_builtin(self.options.with_tevent)}",
            ])
        tc.generate()
        pkg = PkgConfigDeps(self)
        pkg.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self,"COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.components["verto"].set_property("pkg_config_name", "libverto")
        self.cpp_info.components["verto"].libs = ["verto"]
        if self.settings.os == "Linux":
            self.cpp_info.components["verto"].system_libs.append("dl")
            if self.options.pthread:
                self.cpp_info.components["verto"].system_libs.append("pthread")

        if self.options.with_glib == "builtin":
            self.cpp_info.components["verto"].requires.append("glib::glib")
        elif self.options.with_glib:
            self.cpp_info.components["verto-glib"].set_property("pkg_config_name", "libverto-glib")
            self.cpp_info.components["verto-glib"].libs = ["verto-glib"]
            self.cpp_info.components["verto-glib"].requires = ["verto", "glib::glib"]

        if self.options.with_libev == "builtin":
            self.cpp_info.components["verto"].requires.append("libev::libev")
        elif self.options.with_libev:
            self.cpp_info.components["verto-libev"].set_property("pkg_config_name", "libverto-libev")
            self.cpp_info.components["verto-libev"].libs = ["verto-libev"]
            self.cpp_info.components["verto-libev"].requires = ["verto", "libev::libev"]

        if self.options.with_libevent == "builtin":
            self.cpp_info.components["verto"].requires.append("libevent::libevent")
        elif self.options.with_libevent:
            self.cpp_info.components["verto-libevent"].set_property("pkg_config_name", "libverto-libevent")
            self.cpp_info.components["verto-libevent"].libs = ["verto-libevent"]
            self.cpp_info.components["verto-libevent"].requires = ["verto", "libevent::libevent"]

        if self.options.with_tevent:
            self.cpp_info.components["verto-tevent"].set_property("pkg_config_name", "libverto-tevent")
            self.cpp_info.components["verto-tevent"].libs = ["verto-tevent"]
            self.cpp_info.components["verto-tevent"].requires = ["verto", "tevent::tevent"]
