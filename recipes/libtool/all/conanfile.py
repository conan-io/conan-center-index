import re

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, replace_in_file, rmdir, rm, rename, load, save
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.errors import ConanException

required_conan_version = ">=1.51.3"


class LibtoolConan(ConanFile):
    name = "libtool"
    description = "GNU libtool is a generic library support script."
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/libtool/"
    topics = ("libtool", "configure", "library", "shared", "static")
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
        # TODO: Remove for Conan v2
        return getattr(self, "settings_build", self.settings)

    @property
    def win_bash(self):
        return self._settings_build.os == "Windows"

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            try:
                del self.options.fPIC
            except ValueError:
                pass

    def configure(self):
        if self.settings.os == "Windows":
            try:
                del self.options.fPIC
            except ValueError:
                pass
        try:
            del self.settings.compiler.libcxx  # for plain C projects only
        except ValueError:
            pass
        try:
            del self.settings.compiler.cppstd  # for plain C projects only
        except ValueError:
            pass

    def layout(self):
        basic_layout(self, src_folder="libtool")

    def requirements(self):
        self.requires("automake/1.16.5")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.tool_requires("msys2/cci.latest")
        self.tool_requires("gnu-config/cci.20210814")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        for dep in self.dependencies.build.values():
            copy(self, "config.*", dep.cpp_info.bindirs[0], self.source_path.joinpath("build-aux"))

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--datarootdir=${prefix}/res",
            "--enable-ltdl-install",
        ])

        if is_msvc(self):
            build = "{}-{}-{}".format(
                "x86_64" if self._settings_build.arch == "x86_64" else "i686",
                "pc" if self._settings_build.arch == "x86" else "win64",
                "mingw32")
            host = "{}-{}-{}".format(
                "x86_64" if self.settings.arch == "x86_64" else "i686",
                "pc" if self.settings.arch == "x86" else "win64",
                "mingw32")
            tc.configure_args.extend([
                f"--build={build}",
                f"--host={host}",
            ])
            if Version(str(self._settings_build.compiler.version)) >= "12":
                tc.extra_cxxflags.append("-FS")

        if self.options.shared and self.settings.os == "Windows":
            tc.extra_defines.append("LIBLTDL_DLL_IMPORT")

        env = tc.environment()
        if is_msvc(self):
            env.define("LD", "link")
            env.define("CXXCPP", "cl -nologo -EP")
            env.define("CPP", "cl -nologo -EP")
            env.define("AR", f"{unix_path(self, self.conf.get('tools.automake:ar-lib'))} lib")
            env.define("LD", "link")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")

        tc.generate(env)

        deps = AutotoolsDeps(self)
        deps.generate()

        ms = VirtualBuildEnv(self)
        ms.generate(scope="build")

    def build(self):
        apply_conandata_patches(self)

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING*", src = self.source_folder, dst = self.package_path.joinpath("licenses"))
        autotools = Autotools(self)
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])  # Need to specify the `DESTDIR` as a Unix path, aware of the subsystem

        if is_apple_os(self):
            fix_apple_shared_install_name(self)

        rm(self, "*.la", self.package_folder, recursive=True)
        rmdir(self, self.package_path.joinpath("res", "info"))
        rmdir(self, self.package_path.joinpath("res", "man"))

        files = (
            self.package_path.joinpath("bin", "libtool"),
            self.package_path.joinpath("bin", "libtoolize"),
        )
        replaces = {
            "GREP": "/usr/bin/env grep",
            "EGREP": "/usr/bin/env grep -E",
            "FGREP": "/usr/bin/env grep -F",
            "SED": "/usr/bin/env sed",
        }
        for file in files:
            contents = load(self, str(file))
            for key, repl in replaces.items():
                contents, nb1 = re.subn("^{}=\"[^\"]*\"".format(key), "{}=\"{}\"".format(key, repl), contents, flags=re.MULTILINE)
                contents, nb2 = re.subn("^: \\$\\{{{}=\"[^$\"]*\"\\}}".format(key), ": ${{{}=\"{}\"}}".format(key, repl), contents, flags=re.MULTILINE)
                if nb1 + nb2 == 0:
                    raise ConanException("Failed to find {} in {}".format(key, repl))
            save(self, str(file))

        if is_msvc(self) and self.options.shared:
            rename(self, self.package_path.joinpath("lib", "ltdl.dll.lib"), self.package_path.joinpath("lib", "ltdl.lib"))

        # allow libtool to link static libs into shared for more platforms
        libtool_m4 = self.package_path.joinpath("res", "aclocal", "libtool.m4")
        method_pass_all = "lt_cv_deplibs_check_method=pass_all"
        replace_in_file(self, libtool_m4, "lt_cv_deplibs_check_method='file_magic ^x86 archive import|^x86 DLL'", method_pass_all)
        replace_in_file(self, libtool_m4, "lt_cv_deplibs_check_method='file_magic file format (pei*-i386(.*architecture: i386)?|pe-arm-wince|pe-x86-64)'", method_pass_all)

    def package_info(self):
        self.cpp_info.libs = ["ltdl"]

        if self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.defines = ["LIBLTDL_DLL_IMPORT"]
        else:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["dl"]

        bin_path = self.package_path.joinpath("bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(str(bin_path))

        self.output.info(f"Defining LIBTOOL_PREFIX environment variable: {self.package_path}")
        self.env_info.LIBTOOL_PREFIX = str(self.package_path)
        self.buildenv_info.define_path("LIBTOOL_PREFIX", str(self.package_path))

        dataroot_path = self.package_path.joinpath("res")
        self.output.info(f"Defining LIBTOOL_DATADIR environment variable: {dataroot_path}")
        self.env_info.LIBTOOL_DATADIR = str(dataroot_path)
        self.buildenv_info.define_path("LIBTOOL_DATADIR", str(dataroot_path))

        pkg_path = dataroot_path.joinpath("libtool", "build-aux")
        self.output.info(f"Defining LIBTOOL_PKGAUXDIR environment variable: {pkg_path}")
        self.env_info.LIBTOOL_PKGAUXDIR = str(pkg_path)
        self.buildenv_info.define_path("LIBTOOL_PKGAUXDIR", str(pkg_path))

        pkgltdl_path = dataroot_path.joinpath("libtool")
        self.output.info(f"Defining LIBTOOL_PKGLTDLDIR environment variable: {pkgltdl_path}")
        self.env_info.LIBTOOL_PKGLTDLDIR = str(pkgltdl_path)
        self.buildenv_info.define_path("LIBTOOL_PKGLTDLDIR", str(pkgltdl_path))

        aclocal_path = dataroot_path.joinpath("aclocal")
        self.output.info(f"Defining ACLOCAL_PATH environment variable: {aclocal_path}")
        self.env_info.ACLOCAL_PATH = str(aclocal_path)
        self.buildenv_info.define_path("ACLOCAL_PATH", str(aclocal_path))
        self.output.info(f"Defining LIBTOOL_ACLOCALDIR environment variable: {aclocal_path}")
        self.env_info.LIBTOOL_ACLOCALDIR = str(aclocal_path)
        self.buildenv_info.define_path("LIBTOOL_ACLOCALDIR", str(aclocal_path))
        self.output.info(f"Appending AUTOMAKE_CONAN_INCLUDES environment variable: {aclocal_path}")
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(str(aclocal_path))

        libtoolize_bin = bin_path.joinpath("libtoolize")
        self.output.info(f"Defining LIBTOOLIZE environment variable: {libtoolize_bin}")
        self.env_info.LIBTOOLIZE = str(libtoolize_bin)
        self.buildenv_info.define_path("LIBTOOLIZE", str(libtoolize_bin))

        libtoolize_bin_conf_key = "tools.libtool:libtoolize"
        self.output.info(f"Defining path to libtoolize binary in configuration as `{libtoolize_bin_conf_key}` with value: {libtoolize_bin}")
        self.conf_info.define(libtoolize_bin_conf_key, str(libtoolize_bin))

        libtool_bin = bin_path.joinpath("libtool")
        self.output.info(f"Defining LIBTOOL environment variable: {libtool_bin}")
        self.env_info.LIBTOOL = str(libtool_bin)
        self.buildenv_info.define_path("LIBTOOL", str(libtool_bin))

        libtool_bin_conf_key = "tools.libtool:libtool"
        self.output.info(f"Defining path to libtool binary in configuration as `{libtool_bin_conf_key}` with value: {libtool_bin}")
        self.conf_info.define(libtool_bin_conf_key, str(libtool_bin))
