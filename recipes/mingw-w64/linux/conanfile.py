import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration


class MingwConan(ConanFile):
    name = "mingw-w64"
    description = "MinGW is a contraction of Minimalist GNU for Windows"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mingw-w64.org/doku.php"
    license = "ZPL-2.1", "MIT", "GPL-2.0-or-later"
    topics = ("gcc", "gnu", "unix", "mingw32", "binutils")
    settings = "os", "arch"
    options = {"threads": ["posix", "win32"], "exception": ["seh", "sjlj"], "gcc": ["10.3.0"]}
    default_options = {"threads": "posix", "exception": "seh", "gcc": "10.3.0"}
    no_copy_source = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def validate(self):
        valid_os = self.conan_data["sources"][self.version]["url"].keys()
        if str(self.settings.os) not in valid_os:
            raise ConanInvalidConfiguration("MinGW {} is only supported for the following operating systems: {}"
                                            .format(self.version, valid_os))
        valid_arch = self.conan_data["sources"][self.version]["url"][str(self.settings.os)].keys()
        if str(self.settings.arch) not in valid_arch:
            raise ConanInvalidConfiguration("MinGW {} is only supported for the following architectures on {}: {}"
                                            .format(self.version, str(self.settings.os), valid_arch))
        if self._settings_build.os == "Linux":
            if "gcc" in self.conan_data["sources"][self.version]["url"][str(self.settings.os)][str(self.settings.arch)]:
                valid_gcc = self.conan_data["sources"][self.version]["url"][str(self.settings.os)][str(self.settings.arch)]["gcc"].keys()
                if str(self.options.gcc) not in valid_gcc:
                    raise ConanInvalidConfiguration("gcc version {} is not in the list of valid versions: {}"
                                                    .format(str(self.options.gcc), valid_gcc))

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.build_requires("7zip/19.00")
        # else:
        #     self.build_requires("gmp/6.2.1")
        #     self.build_requires("mpfr/4.1.0")
        #     self.build_requires("mpc/1.2.0")

    def _download_source(self):
        arch_data = self.conan_data["sources"][self.version]["url"][str(self.settings.os)][str(self.settings.arch)]

        if self.settings.os == "Windows":
            url = arch_data[str(self.options.threads)][str(self.options.exception)]
            self.output.info("Downloading: %s" % url["url"])
            tools.download(url["url"], "file.7z", sha256=url["sha256"])
            self.run("7z x file.7z")
            os.remove('file.7z')
        else:
            for package in arch_data:
                if package == "gcc":
                    continue
                self.output.info("Downloading {} from {}".format(package, arch_data[package]['url']))
                tools.get(**arch_data[package], strip_root=True, destination=os.path.join(self.build_folder, "sources", package))
            # Download gcc version
            gcc_data = self.conan_data["sources"][self.version]["url"][str(self.settings.os)][str(self.settings.arch)]["gcc"][str(self.options.gcc)]
            tools.get(**gcc_data, strip_root=True, destination=os.path.join(self.build_folder, "sources", "gcc"))

    @property
    def _target_tag(self):
        return "x86_64-w64-mingw32"

    def build(self):
        # Source should be downloaded in the build step since it depends on specific options
        self._download_source()

        if self.settings.os == "Windows":
            return

        target_tag = self._target_tag
        host_tag = "x86_64-linux-gnu"

        # We currently cannot build with multilib and threads=posix. Otherwise we get the gcc compile error:
        # checking for ld that supports -Wl,--gc-sections... configure: error: Link tests are not allowed after GCC_NO_EXECUTABLES.
        # Makefile:11275: recipe for target 'configure-target-libstdc++-v3' failed
        build_multilib = False

        # Instructions see:
        # https://sourceforge.net/p/mingw-w64/code/HEAD/tree/trunk/mingw-w64-doc/howto-build/mingw-w64-howto-build.txt
        # and
        # https://sourceforge.net/p/mingw-w64/code/HEAD/tree/trunk/mingw-w64-doc/howto-build/mingw-w64-howto-build-adv.txt
        # also good to see specific commands:
        # https://android.googlesource.com/platform/prebuilts/gcc/linux-x86/host/x86_64-w64-mingw32-4.8/+/lollipop-dev/build-mingw64-toolchain.sh

        # add binutils to path. Required for gcc build
        env = {"PATH": os.environ["PATH"] + ":" + os.path.join(self.package_folder, "bin")}

        with tools.environment_append(env):
            self.output.info("Building gmp ...")
            os.mkdir(os.path.join(self.build_folder, "gmp"))
            with tools.chdir(os.path.join(self.build_folder, "gmp")):
                autotools = AutoToolsBuildEnvironment(self)
                conf_args = [
                    "--enable-silent-rules",
                    "--disable-shared"
                ]
                autotools.configure(configure_dir=os.path.join(self.build_folder, "sources", "gmp"),
                                    args=conf_args, target=False, host=False, build=False)
                autotools.make()
                autotools.install()

            self.output.info("Building mpfr ...")
            os.mkdir(os.path.join(self.build_folder, "mpfr"))
            with tools.chdir(os.path.join(self.build_folder, "mpfr")):
                autotools = AutoToolsBuildEnvironment(self)
                conf_args = [
                    "--enable-silent-rules",
                    "--disable-shared",
                    "--with-gmp={}".format(self.package_folder)
                ]
                autotools.configure(configure_dir=os.path.join(self.build_folder, "sources", "mpfr"),
                                    args=conf_args, target=False, host=False, build=False)
                autotools.make()
                autotools.install()

            self.output.info("Building mpc ...")
            os.mkdir(os.path.join(self.build_folder, "mpc"))
            with tools.chdir(os.path.join(self.build_folder, "mpc")):
                autotools = AutoToolsBuildEnvironment(self)
                conf_args = [
                    "--enable-silent-rules",
                    "--disable-shared",
                    "--with-gmp={}".format(self.package_folder),
                    "--with-mpfr={}".format(self.package_folder)
                ]
                autotools.configure(configure_dir=os.path.join(self.build_folder, "sources", "mpc"),
                                    args=conf_args, target=False, host=False, build=False)
                autotools.make()
                autotools.install()
            with_gmp_mpfc_mpc = [
                "--with-gmp={}".format(self.package_folder),
                "--with-mpfr={}".format(self.package_folder),
                "--with-mpc={}".format(self.package_folder)
            ]
            # with_gmp_mpfc_mpc = [
            #    "--with-gmp=system",
            #    "--with-gmp-prefix={}".format(self.deps_cpp_info["gmp"].rootpath.replace("\\", "/")),
            #    "--with-mpfr=system",
            #    "--with-mpfr-prefix={}".format(self.deps_cpp_info["mpfr"].rootpath.replace("\\", "/")),
            #    "--with-mpc=system",
            #    "--with-mpc-prefix={}".format(self.deps_cpp_info["mpc"].rootpath.replace("\\", "/"))
            # ]

            self.output.info("Building binutils ...")
            os.mkdir(os.path.join(self.build_folder, "binutils"))
            with tools.chdir(os.path.join(self.build_folder, "binutils")):
                autotools = AutoToolsBuildEnvironment(self)
                conf_args = [
                    "--enable-silent-rules",
                    "--with-sysroot={}".format(self.package_folder),
                    "--disable-nls",
                    "--disable-shared"
                ]
                if build_multilib:
                    conf_args.append("--enable-targets=x86_64-w64-mingw32,i686-w64-mingw32")
                conf_args.extend(with_gmp_mpfc_mpc)
                autotools.configure(configure_dir=os.path.join(self.build_folder, "sources", "binutils"),
                                    args=conf_args, target=target_tag, host=False, build=False)
                autotools.make()
                autotools.install()

            self.output.info("Building mingw-w64-tools ...")
            os.mkdir(os.path.join(self.build_folder, "mingw-w64-tools"))
            with tools.chdir(os.path.join(self.build_folder, "mingw-w64-tools")):
                autotools = AutoToolsBuildEnvironment(self)
                conf_args = []
                autotools.configure(configure_dir=os.path.join(self.build_folder, "sources", "mingw-w64", "mingw-w64-tools", "widl"),
                                    args=conf_args, target=target_tag, host=False, build=False)
                autotools.make()
                autotools.install()

            self.output.info("Building mingw-w64-headers ...")
            os.mkdir(os.path.join(self.build_folder, "mingw-w64-headers"))
            with tools.chdir(os.path.join(self.build_folder, "mingw-w64-headers")):
                autotools = AutoToolsBuildEnvironment(self)
                conf_args = [
                    "--enable-silent-rules",
                    "--with-widl={}".format(os.path.join(self.package_folder, "bin")),
                    "--enable-sdk=all",
                    "--prefix={}".format(os.path.join(self.package_folder, target_tag))
                ]
                autotools.configure(configure_dir=os.path.join(self.build_folder, "sources", "mingw-w64", "mingw-w64-headers"),
                                    args=conf_args, target=False, host=target_tag, build=host_tag)
                autotools.make()
                autotools.install()
                # Step 3) GCC requires the x86_64-w64-mingw32 directory be mirrored as a
                # directory 'mingw' in the same root.  So, if using configure default
                # /usr/local, type:
                #     ln -s /usr/local/x86_64-w64-mingw32 /usr/local/mingw
                #     or, for sysroot, type:
                #     ln -s /mypath/x86_64-w64-mingw32 /mypath/mingw
                self.run("ln -s {} {}".format(os.path.join(self.package_folder, target_tag),
                                              os.path.join(self.package_folder, 'mingw')))
                # Step 5) Symlink x86_64-w64-mingw32/lib directory as x86_64-w64-mingw32/lib64:
                # ln -s /usr/local/x86_64-w64-mingw32/lib /usr/local/x86_64-w64-mingw32/lib64
                # or, for sysroot:
                #     ln -s /mypath/x86_64-w64-mingw32/lib /mypath/x86_64-w64-mingw32/lib64
                self.run("ln -s {} {}".format(os.path.join(self.package_folder, target_tag, 'lib'),
                                              os.path.join(self.package_folder, target_tag, 'lib64')))

            self.output.info("Building core gcc ...")
            os.mkdir(os.path.join(self.build_folder, "gcc"))
            with tools.chdir(os.path.join(self.build_folder, "gcc")):
                autotools_gcc = AutoToolsBuildEnvironment(self)
                conf_args = [
                    "--enable-silent-rules",
                    "--enable-languages=c,c++",
                    "--with-sysroot={}".format(self.package_folder),
                    "--disable-shared"
                ]
                if build_multilib:
                    conf_args.append("--enable-targets=all")
                    conf_args.append("--enable-multilib")
                else:
                    conf_args.append("--disable-multilib")
                conf_args.extend(with_gmp_mpfc_mpc)
                if self.options.exception == "sjlj":
                    conf_args.append("--enable-sjlj-exceptions")
                if self.options.threads == "posix":
                    # Some specific options which need to be set for posix thread. Otherwise it fails compiling.
                    conf_args.extend([
                        "--enable-silent-rules",
                        "--enable-threads=posix",
                        # Not 100% sure why, but the following options are required, otherwise
                        # gcc fails to build with posix threads
                    ])
                autotools_gcc.configure(configure_dir=os.path.join(self.build_folder, "sources", "gcc"),
                                        args=conf_args, target=target_tag, host=False, build=False)
                autotools_gcc.make(target="all-gcc")
                autotools_gcc.make(target="install-gcc")

            env_compiler = dict(env)
            # The CC and CXX compiler must be set to the mingw compiler. Conan already sets CC and CXX, therefore we need to overwrite it.
            # If the wrong compiler is used for mingw-w64-crt, then you will get the error
            # configure: Please check if the mingw-w64 header set and the build/host option are set properly.
            env_compiler["CC"] = target_tag + "-gcc"
            env_compiler["CXX"] = target_tag + "-g++"
            with tools.environment_append(env_compiler):
                self.output.info("Building mingw-w64-crt ...")
                os.mkdir(os.path.join(self.build_folder, "mingw-w64-crt"))
                with tools.chdir(os.path.join(self.build_folder, "mingw-w64-crt")):
                    autotools = AutoToolsBuildEnvironment(self)
                    conf_args = [
                        "--enable-silent-rules",
                        "--prefix={}".format(os.path.join(self.package_folder, target_tag)),
                        "--with-sysroot={}".format(self.package_folder)
                    ]
                    if build_multilib:
                        conf_args.append("--enable-lib32")
                    autotools.configure(configure_dir=os.path.join(self.build_folder, "sources", "mingw-w64", "mingw-w64-crt"),
                                        args=conf_args, target=False, host=target_tag, build=False,
                                        use_default_install_dirs=False)
                    autotools.make()
                    autotools.install()

                if self.options.threads == "posix":
                    self.output.info("Building mingw-w64-libraries-winpthreads ...")
                    os.mkdir(os.path.join(self.build_folder, "mingw-w64-libraries-winpthreads"))
                    with tools.chdir(os.path.join(self.build_folder, "mingw-w64-libraries-winpthreads")):
                        autotools = AutoToolsBuildEnvironment(self)
                        conf_args = [
                            "--enable-silent-rules",
                            "--disable-shared",
                            "--prefix={}".format(os.path.join(self.package_folder, target_tag))
                        ]
                        autotools.configure(configure_dir=os.path.join(self.build_folder, "sources", "mingw-w64", "mingw-w64-libraries", "winpthreads"),
                                            args=conf_args, target=False, host=target_tag, build=False)
                        autotools.make()
                        autotools.install()

            self.output.info("Building libgcc ...")
            with tools.chdir(os.path.join(self.build_folder, "gcc")):
                autotools_gcc.make()
                autotools_gcc.install()

        self.output.info("Building done!")

    def package(self):
        if self.settings.os == "Windows":
            target = "mingw64" if self.settings.arch == "x86_64" else "mingw32"
            self.copy("*", dst="", src=target)
            tools.rmdir(target)
            tools.rmdir(os.path.join(self.package_folder, "share"))
        else:
            self.copy("COPYING", src=os.path.join(self.build_folder, "sources", "mingw-w64"), dst="licenses")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "x86_64-w64-mingw32", "lib"), "*.la")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "x86_64-w64-mingw32", "lib32"), "*.la")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "bin", "gcc", "x86_64-w64-mingw32", "10.3.0"), "*.la")
            tools.rmdir(os.path.join(self.package_folder, "share", "man"))
            tools.rmdir(os.path.join(self.package_folder, "share", "doc"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            # Remove symlinks, we need to create them in the package_info step
            os.unlink(os.path.join(self.package_folder, 'mingw'))
            os.unlink(os.path.join(self.package_folder, self._target_tag, 'lib64'))

    def package_info(self):
        if getattr(self, "settings_target", None):
            if self.settings_target.compiler != "gcc":
                raise ConanInvalidConfiguration("Only GCC is allowed as compiler.")
            if str(self.settings_target.compiler.threads) != str(self.options.threads):
                raise ConanInvalidConfiguration("Build requires 'mingw' provides binaries for gcc "
                                                "with threads={}, your profile:host declares "
                                                "threads={}, please use the same value for both."
                                                .format(self.options.threads,
                                                        self.settings_target.compiler.threads))
            if str(self.settings_target.compiler.exception) != str(self.options.exception):
                raise ConanInvalidConfiguration("Build requires 'mingw' provides binaries for gcc "
                                                "with exception={}, your profile:host declares "
                                                "exception={}, please use the same value for both."
                                                .format(self.options.exception,
                                                        self.settings_target.compiler.exception))

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.env_info.MINGW_HOME = str(self.package_folder)

        if self.settings.os == "Windows":
            self.env_info.CONAN_CMAKE_GENERATOR = "MinGW Makefiles"
            self.env_info.CXX = os.path.join(self.package_folder, "bin", "g++.exe").replace("\\", "/")
            self.env_info.CC = os.path.join(self.package_folder, "bin", "gcc.exe").replace("\\", "/")
            self.env_info.LD = os.path.join(self.package_folder, "bin", "ld.exe").replace("\\", "/")
            self.env_info.NM = os.path.join(self.package_folder, "bin", "nm.exe").replace("\\", "/")
            self.env_info.AR = os.path.join(self.package_folder, "bin", "ar.exe").replace("\\", "/")
            self.env_info.AS = os.path.join(self.package_folder, "bin", "as.exe").replace("\\", "/")
            self.env_info.STRIP = os.path.join(self.package_folder, "bin", "strip.exe").replace("\\", "/")
            self.env_info.RANLIB = os.path.join(self.package_folder, "bin", "ranlib.exe").replace("\\", "/")
            self.env_info.STRINGS = os.path.join(self.package_folder, "bin", "strings.exe").replace("\\", "/")
            self.env_info.OBJDUMP = os.path.join(self.package_folder, "bin", "objdump.exe").replace("\\", "/")
            self.env_info.GCOV = os.path.join(self.package_folder, "bin", "gcov.exe").replace("\\", "/")
        else:
            prefix = os.path.join(self.package_folder, "bin", self._target_tag + "-")
            self.env_info.CC = prefix + "gcc"
            self.env_info.CXX = prefix + "g++"
            self.env_info.CPP = prefix + "cpp"
            self.env_info.AR = prefix + "ar"
            self.env_info.AS = prefix + "as"
            self.env_info.GDB = prefix + "gdb"
            self.env_info.LD = prefix + "ld"
            self.env_info.NM = prefix + "nm"
            self.env_info.OBJCOPY = prefix + "objcopy"
            self.env_info.OBJDUMP = prefix + "objdump"
            self.env_info.RANLIB = prefix + "ranlib"
            self.env_info.SIZE = prefix + "size"
            self.env_info.STRINGS = prefix + "strings"
            self.env_info.STRIP = prefix + "strip"
            self.env_info.GCOV = prefix + "gcov"
            self.env_info.RC = prefix + "windres"
            # Symlinks cannot be created in package step, otherwise the link target is wrong.
            if not os.path.exists(os.path.join(self.package_folder, 'mingw')):
                self.run("ln -s {} {}".format(os.path.join(self.package_folder, self._target_tag),
                                              os.path.join(self.package_folder, 'mingw')))
            if not os.path.exists(os.path.join(self.package_folder, self._target_tag, 'lib64')):
                self.run("ln -s {} {}".format(os.path.join(self.package_folder, self._target_tag, 'lib'),
                                              os.path.join(self.package_folder, self._target_tag, 'lib64')))
