from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rm, rmdir, export_conandata_patches, apply_conandata_patches
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import Autotools, AutotoolsToolchain,AutotoolsDeps, PkgConfigDeps
from conan.tools.microsoft import is_msvc
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.33.0"


class LibVertoConan(ConanFile):
    name = "libverto"
    description = "An async event loop abstraction library."
    homepage = "https://github.com/latchset/libverto"
    topics = ("libverto", "async", "eventloop")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
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
    settings = "os", "arch", "compiler", "build_type"

   

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

    def layout(self):
        basic_layout(self, src_folder="src")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.pthread

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("libverto does not support Visual Studio")
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Shared libraries are not supported on Windows")

        if not self._backend_dict[str(self.options.default)]:
            raise ConanInvalidConfiguration("Default backend({}) must be available".format(self.options.default))

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

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def requirements(self):
        if self.options.with_glib:
            self.requires("glib/2.74.21")
        if self.options.with_libevent:
            self.requires("libevent/2.1.12")
        if self.options.with_libev:
            self.requires("libev/4.33")
        if self.options.with_tevent:
            # FIXME: missing tevent recipe
            raise ConanInvalidConfiguration("tevent is not (yet) available on conan-center")

    def build_requirements(self):
        self.tool_requires("pkgconf/1.9.3")
        self.tool_requires("libtool/2.4.7")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

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

        env = tc.environment()
        # if is_msvc(self):
        #     # FIXME: Use the conf once https://github.com/conan-io/conan-center-index/pull/12898 is merged
        #     # env.define("AR", f"{unix_path(self, self.conf.get('tools.automake:ar-lib'))}")
        #     [version_major, version_minor, _] = self.dependencies.direct_build['automake'].ref.version.split(".", 2)
        #     automake_version = f"{version_major}.{version_minor}"
        #     ar_wrapper = unix_path(self, os.path.join(self.dependencies.direct_build['automake'].cpp_info.resdirs[0], f"automake-{automake_version}", "ar-lib"))
        #     env.define("CC", "{} cl -nologo".format(unix_path(self.dependencies.direct_build["automake"].compile))) 
        #     env.define("CXX", "{} cl -nologo".format(unix_path(self.deps_user_info["automake"].compile))) 
        #     env.define("LD", "link -nologo") 
        #     env.define("AR", f"{ar_wrapper} \"lib -nologo\"")

        tc.generate()
        deps = AutotoolsDeps(self)
        deps.generate()
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

    def package_id(self):
        del self.info.options.default

    def package_info(self):
        self.cpp_info.components["verto"].libs = ["verto"]
        self.cpp_info.components["verto"].names["pkg_config"] = "libverto"
        if self.settings.os == "Linux":
            self.cpp_info.components["verto"].system_libs.append("dl")
            if self.options.pthread:
                self.cpp_info.components["verto"].system_libs.append("pthread")

        if self.options.with_glib == "builtin":
            self.cpp_info.components["verto"].requires.append("glib::glib")
        elif self.options.with_glib:
            self.cpp_info.components["verto-glib"].libs = ["verto-glib"]
            self.cpp_info.components["verto-glib"].names["pkg_config"] = "libverto-glib"
            self.cpp_info.components["verto-glib"].requires = ["verto", "glib::glib"]

        if self.options.with_libev == "builtin":
            self.cpp_info.components["verto"].requires.append("libev::libev")
        elif self.options.with_libev:
            self.cpp_info.components["verto-libev"].libs = ["verto-libev"]
            self.cpp_info.components["verto-libev"].names["pkg_config"] = "libverto-libev"
            self.cpp_info.components["verto-libev"].requires = ["verto", "libev::libev"]

        if self.options.with_libevent == "builtin":
            self.cpp_info.components["verto"].requires.append("libevent::libevent")
        elif self.options.with_libevent:
            self.cpp_info.components["verto-libevent"].libs = ["verto-libevent"]
            self.cpp_info.components["verto-libevent"].names["pkg_config"] = "libverto-libevent"
            self.cpp_info.components["verto-libevent"].requires = ["verto", "libevent::libevent"]

        if self.options.with_tevent:
            self.cpp_info.components["verto-tevent"].libs = ["verto-tevent"]
            self.cpp_info.components["verto-tevent"].names["pkg_config"] = "libverto-tevent"
            self.cpp_info.components["verto-tevent"].requires = ["verto", "tevent::tevent"]

        self.user_info.backends = ",".join(tuple(backend for backend, opt in self._backend_dict.items() if opt != False))
