import os
from contextlib import contextmanager

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import chdir, copy, get, mkdir, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class MingwConan(ConanFile):
    name = "mingw-w64"
    description = ("This package provides a MinGW-w64 environment with a GCC toolchain "
                   "for cross-compilation of native Windows binaries from Linux.")
    license = ("ZPL-2.1", "MIT", "GPL-2.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.mingw-w64.org/"
    topics = ("gcc", "gnu", "unix", "mingw32", "binutils")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "threads": ["posix", "win32"],
        "exception": ["seh", "sjlj"],
        "gcc": ["10.5.0"],
    }
    default_options = {
        "threads": "posix",
        "exception": "seh",
        "gcc": "10.5.0",
    }
    options_description = {
        "threads": "Threading model: posix or win32",
        "exception": "Exception model: seh (Structured Exception Handling) or sjlj (setjmp/longjmp)",
        "gcc": "GCC version provided by MinGW-w64",
    }

    short_paths = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        valid_os = ["Linux", "FreeBSD"]
        if str(self.settings.os) not in valid_os:
            raise ConanInvalidConfiguration(
                f"MinGW {self.version} is only supported for the following operating systems: {valid_os}"
            )
        valid_arch = ["x86_64"]
        if str(self.settings.arch) not in valid_arch:
            raise ConanInvalidConfiguration(
                f"MinGW {self.version} is only supported for the following architectures on {str(self.settings.os)}: {valid_arch}"
            )

    def build_requirements(self):
        self.tool_requires("m4/1.4.19")
        self.tool_requires("gmp/6.3.0")
        self.tool_requires("mpfr/4.2.0")
        self.tool_requires("mpc/1.3.1")

    def source(self):
        # Source is downloaded in the build step since it depends on specific option values
        pass

    def _download_source(self, package):
        self.output.info(f"Downloading {package} ...")
        info = self.conan_data["sources"][self.version][package]
        if package == "gcc":
            info = info[str(self.options.gcc)]
        destination = os.path.join(self.source_folder, package)
        get(self, **info, strip_root=True, destination=destination)
        return destination

    @property
    def _build_multilib(self):
        # We currently cannot build with multilib and threads=posix. Otherwise we get the gcc compile error:
        # checking for ld that supports -Wl,--gc-sections... configure: error: Link tests are not allowed after GCC_NO_EXECUTABLES.
        # Makefile:11275: recipe for target 'configure-target-libstdc++-v3' failed
        return False

    @property
    def _host_tag(self):
        return "x86_64-linux-gnu"

    @property
    def _target_tag(self):
        return "x86_64-w64-mingw32"

    def _get_package_root(self, p):
        return self.dependencies.build[p].package_folder.replace("\\", "/")

    @property
    def _with_gmp_mpfr_mpc(self):
        return [
            f"--with-gmp={self._get_package_root('gmp')}",
            f"--with-mpfr={self._get_package_root('mpfr')}",
            f"--with-mpc={self._get_package_root('mpc')}",
        ]

    def generate(self):
        # Instructions see:
        # https://sourceforge.net/p/mingw-w64/code/HEAD/tree/trunk/mingw-w64-doc/howto-build/mingw-w64-howto-build.txt
        # and
        # https://sourceforge.net/p/mingw-w64/code/HEAD/tree/trunk/mingw-w64-doc/howto-build/mingw-w64-howto-build-adv.txt
        # also good to see specific commands:
        # https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/host/x86_64-w64-mingw32-4.8/+/lollipop-dev/build-mingw64-toolchain.sh

        # Add binutils to path. Required for gcc build.
        env = Environment()
        env.prepend_path("PATH", os.path.join(self.package_folder, "bin"))
        env.vars(self).save_script("conanbuild_package_bin_path")

        venv = VirtualBuildEnv(self)
        venv.generate()

        deps = PkgConfigDeps(self)
        deps.generate()

        self.output.info("Generating for binutils ...")
        tc = AutotoolsToolchain(self, namespace="binutils")
        tc.configure_args += [
            f"--target={self._target_tag}",
            f"--with-sysroot={self.package_folder}",
            "--enable-silent-rules",
            "--disable-nls",
            "--disable-shared",
        ]
        if self._build_multilib:
            tc.configure_args.append("--enable-targets=x86_64-w64-mingw32,i686-w64-mingw32")
        tc.configure_args.extend(self._with_gmp_mpfr_mpc)
        tc.generate()

        self.output.info("Generating for mingw-w64-tools ...")
        tc = AutotoolsToolchain(self, namespace="mingw-w64-tools")
        tc.configure_args += [
            f"--target={self._target_tag}"
        ]
        tc.generate()

        self.output.info("Generating for mingw-w64-headers ...")
        tc = AutotoolsToolchain(self, namespace="mingw-w64-headers")
        tc.configure_args += [
            f"--host={self._target_tag}",
            f"--build={self._host_tag}",
            f"--prefix=/{self._target_tag}",
            f"--with-widl={os.path.join(self.package_folder, 'bin')}",
            "--enable-silent-rules",
            "--enable-sdk=all",
        ]
        tc.generate()

        self.output.info("Generating for core gcc ...")
        tc = AutotoolsToolchain(self, namespace="gcc")
        tc.configure_args += [
            f"--target={self._target_tag}",
            f"--with-sysroot={self.package_folder}",
            "--disable-shared",
            "--enable-silent-rules",
            "--enable-languages=c,c++",
        ]
        if self._build_multilib:
            tc.configure_args.append("--enable-targets=all")
            tc.configure_args.append("--enable-multilib")
        else:
            tc.configure_args.append("--disable-multilib")
        tc.configure_args.extend(self._with_gmp_mpfr_mpc)
        if self.options.exception == "sjlj":
            tc.configure_args.append("--enable-sjlj-exceptions")
        if self.options.threads == "posix":
            # Some specific options which need to be set for posix thread. Otherwise it fails to compile.
            tc.configure_args.extend([
                "--enable-silent-rules",
                "--enable-threads=posix",
                # Not 100% sure why, but the following options are required, otherwise
                # gcc fails to build with posix threads
            ])
        tc.libs = []
        tc.generate()

        self.output.info("Generating for mingw-w64-crt ...")
        tc = AutotoolsToolchain(self, namespace="mingw-w64-crt")
        tc.configure_args += [
            f"--host={self._target_tag}",
            f"--prefix=/{self._target_tag}",
            f"--with-sysroot={self.package_folder}",
            f"CC={self._target_tag}-gcc",
            f"CXX={self._target_tag}-g++",
            "--enable-silent-rules",
        ]
        if self._build_multilib:
            tc.configure_args.append("--enable-lib32")
        tc.generate()

        if self.options.threads == "posix":
            self.output.info("Generating for mingw-w64-libraries-winpthreads ...")
            tc = AutotoolsToolchain(self, namespace="mingw-w64-libraries-winpthreads")
            tc.configure_args += [
                f"--host={self._target_tag}",
                f"--prefix=/{self._target_tag}",
                f"CC={self._target_tag}-gcc",
                f"CXX={self._target_tag}-g++",
                "--enable-silent-rules",
                "--disable-shared",
            ]
            tc.generate()

    @contextmanager
    def _build_namespace(self, namespace):
        self.output.info(f"Building {namespace} ...")
        build_dir = os.path.join(self.build_folder, namespace)
        mkdir(self, build_dir)
        with chdir(self, build_dir):
            yield Autotools(self, namespace=namespace)

    def build(self):
        binutils_source = self._download_source("binutils")
        with self._build_namespace("binutils") as autotools:
            autotools.configure(binutils_source)
            autotools.make()
            autotools.install()

        mingw_w64_source = self._download_source("mingw-w64")
        with self._build_namespace("mingw-w64-tools") as autotools:
            autotools.configure(os.path.join(mingw_w64_source, "mingw-w64-tools", "widl"))
            autotools.make()
            autotools.install()

        with self._build_namespace("mingw-w64-headers") as autotools:
            autotools.configure(os.path.join(mingw_w64_source, "mingw-w64-headers"))
            autotools.make()
            autotools.install()

        # Step 3) GCC requires the x86_64-w64-mingw32 directory be mirrored as a
        # directory 'mingw' in the same root.  So, if using configure default
        # /usr/local, type:
        #     ln -s /usr/local/x86_64-w64-mingw32 /usr/local/mingw
        #     or, for sysroot, type:
        #     ln -s /mypath/x86_64-w64-mingw32 /mypath/mingw
        with chdir(self, self.package_folder):
            os.symlink(self._target_tag, "mingw")

        # Step 5) Symlink x86_64-w64-mingw32/lib directory as x86_64-w64-mingw32/lib64:
        # ln -s /usr/local/x86_64-w64-mingw32/lib /usr/local/x86_64-w64-mingw32/lib64
        # or, for sysroot:
        #     ln -s /mypath/x86_64-w64-mingw32/lib /mypath/x86_64-w64-mingw32/lib64
        with chdir(self, os.path.join(self.package_folder, self._target_tag)):
            os.symlink("lib", "lib64")

        gcc_source = self._download_source("gcc")
        with self._build_namespace("gcc") as autotools:
            autotools.configure(gcc_source)
            autotools.make(target="all-gcc")
            autotools.install(target="install-gcc")

        with self._build_namespace("mingw-w64-crt") as autotools:
            autotools.configure(os.path.join(mingw_w64_source, "mingw-w64-crt"))
            autotools.make()
            autotools.install()

        if self.options.threads == "posix":
            with self._build_namespace("mingw-w64-libraries-winpthreads") as autotools:
                autotools.configure(os.path.join(mingw_w64_source, "mingw-w64-libraries", "winpthreads"))
                autotools.make()
                autotools.install()

        with self._build_namespace("gcc") as autotools:
            autotools.make()
            autotools.install()

        self.output.info("Building done!")

    def package(self):
        copy(self, "COPYING",
             src=os.path.join(self.source_folder, "mingw-w64"),
             dst=os.path.join(self.package_folder, "licenses"))
        rm(self, "*.la", self.package_folder, recursive=True)
        rmdir(self, os.path.join(self.package_folder, "share", "man"))
        rmdir(self, os.path.join(self.package_folder, "share", "doc"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        if getattr(self, "settings_target", None):
            if self.settings_target.compiler != "gcc":
                self.output.warning("Only GCC is allowed as the compiler.")
            if str(self.settings_target.compiler.threads) != str(self.options.threads):
                self.output.warning(
                    f"Build requires 'mingw' provides binaries for gcc with threads={self.options.threads},"
                    f" your profile:host declares threads={self.settings_target.compiler.threads},"
                    " please use the same value for both."
                )
            if str(self.settings_target.compiler.exception) != str(self.options.exception):
                self.output.warning(
                    f"Build requires 'mingw' provides binaries for gcc with exception={self.options.exception},"
                    f" your profile:host declares exception={self.settings_target.compiler.exception},"
                    " please use the same value for both."
                )

        bin_path = os.path.join(self.package_folder, "bin")
        prefix = os.path.join(bin_path, self._target_tag + "-")

        self.buildenv_info.prepend_path("PATH", bin_path)
        self.env_info.PATH.append(bin_path)

        self.buildenv_info.define_path("MINGW_HOME", self.package_folder)
        self.env_info.MINGW_HOME = self.package_folder

        def define_tool_env(var, name):
            self.buildenv_info.define_path(var, prefix + name)
            setattr(self.env_info, var, prefix + name)

        define_tool_env("CC", "gcc")
        define_tool_env("CXX", "g++")
        define_tool_env("CPP", "cpp")
        define_tool_env("AR", "ar")
        define_tool_env("AS", "as")
        define_tool_env("GDB", "gdb")
        define_tool_env("LD", "ld")
        define_tool_env("NM", "nm")
        define_tool_env("OBJCOPY", "objcopy")
        define_tool_env("OBJDUMP", "objdump")
        define_tool_env("RANLIB", "ranlib")
        define_tool_env("SIZE", "size")
        define_tool_env("STRINGS", "strings")
        define_tool_env("STRIP", "strip")
        define_tool_env("GCOV", "gcov")
        define_tool_env("RC", "windres")
        define_tool_env("DLLTOOL", "dlltool")
