from conans import tools, ConanFile, AutoToolsBuildEnvironment, RunEnvironment
import platform
import sys
import os


class SqlcipherConan(ConanFile):
    name = "sqlcipher"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.zetetic.net/sqlcipher/"
    description = "SQLite extension that provides 256 bit AES encryption of database files."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "crypto_library": ["openssl", "libressl"]}
    default_options = {"shared": False, "fPIC": True, "crypto_library": "openssl"}
    topics = ("database", "encryption", "SQLite")
    exports_sources = "patches/*"
    generators = "cmake"
    _source_subfolder = "source_subfolder"


    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("tcl/8.6.10")

    def requirements(self):
        if self.options.crypto_library == "openssl":
            self.requires("openssl/1.1.1d")
        else:
            self.requires("libressl/2.9.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _build_visual(self):
        crypto_dep = self.deps_cpp_info[str(self.options.crypto_library)]
        crypto_incdir = crypto_dep.include_paths[0]
        crypto_libdir = crypto_dep.lib_paths[0]
        libs = map(lambda lib : lib + ".lib", crypto_dep.libs)

        nmake_flags = [
                "TLIBS=\"%s\"" % " ".join(libs),
                "LTLIBPATHS=/LIBPATH:%s" % crypto_libdir,
                "OPTS=\"-I%s -DSQLITE_HAS_CODEC\"" % (crypto_incdir),
                "NO_TCL=1",
                "USE_AMALGAMATION=1",
                "OPT_FEATURE_FLAGS=-DSQLCIPHER_CRYPTO_OPENSSL",
                "TCLSH_CMD=%s" % self.deps_env_info.TCLSH,
                ]

        main_target = "dll" if self.options.shared else "sqlcipher.lib"

        if self.settings.compiler.runtime in ["MD", "MDd"]:
            nmake_flags.append("USE_CRT_DLL=1")
        if self.settings.build_type == "Debug":
            nmake_flags.append("DEBUG=2")
        nmake_flags.append("FOR_WIN10=1")
        platforms = {"x86": "x86", "x86_64": "x64"}
        nmake_flags.append("PLATFORM=%s" % platforms[self.settings.arch.value])
        vcvars = tools.vcvars_command(self.settings)
        self.run("%s && nmake /f Makefile.msc %s %s" % (vcvars, main_target, " ".join(nmake_flags)), cwd=self._source_subfolder)

    def _build_autotools(self):
        self.run('chmod +x configure', cwd=self._source_subfolder)
        absolute_install_dir = os.path.abspath(os.path.join(".", "install"))
        absolute_install_dir = absolute_install_dir.replace("\\", "/")
        autotools_env = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.os == "Linux":
            autotools_env.libs.append("dl")
        autotools_env.defines.extend(["SQLITE_HAS_CODEC", "SQLCIPHER_CRYPTO_OPENSSL"])

        # sqlcipher config.sub does not contain android configurations...
        # elf is the most basic `os' for Android
        host = None
        if self.settings.os == "Android":
            host = "%s-linux-elf" % self.arch_id_str_compiler
        elif self.settings.os == "Windows":
            arch = str(self.settings.arch)
            if arch == "x86":
                arch = "i386"
            host = "%s-pc-mingw32" % arch
        elif self.settings.os == "iOS":
            host = "%s-apple-darwin" % self.settings.arch

        configure_args = self._get_configure_args(absolute_install_dir)
        with tools.chdir(self._source_subfolder):
            # Hack, uname -p returns i386, configure guesses x86_64, we must force i386 so that cross-compilation is correctly detected.
            # Otherwise host/build are the same, and configure tries to launch a sample executable, and fails miserably.
            env_vars = autotools_env.vars
            if self.settings.os == "iOS":
                build = "i386-apple-darwin"
            # same for mingw...
            elif self.settings.os == "Windows":
                build = "x86_64-linux"
                env_vars["config_TARGET_EXEEXT"] = ".exe"
            else:
                build = None
            autotools_env.configure(args=configure_args, host=host, build=build, vars=env_vars)
            if self.settings.os == "Windows":
                # sqlcipher will create .exe for the build machine, which is Linux...
                tools.replace_in_file(os.path.join(self.build_folder, self._source_subfolder, "Makefile"), "BEXE = .exe", "BEXE = ")
            autotools_env.make(args=["install"])

    @property
    def _arch_id_str_compiler(self):
        return {"x86": "i686",
                "armv6": "arm",
                "armv7": "arm",
                "armv7hf": "arm",
                # Hack: config.guess of sqlcipher does not like aarch64
                "armv8": "armv8",
                "mips64": "mips64"}.get(str(self.settings.arch),
                                        str(self.settings.arch))

    def _get_configure_args(self, absolute_install_dir):
        args = [
            "--prefix=%s" % absolute_install_dir,

            self._autotools_bool_arg("shared", self.options.shared),
            self._autotools_bool_arg("static", not self.options.shared),
            "--enable-tempstore=yes",
            "--with-tcl={}".format(os.path.join(self.deps_env_info.TCL_ROOT, "lib"))
        ]
        if self.settings.os == "Windows":
            args.extend(["config_BUILD_EXEEXT='.exe'", "config_TARGET_EXEEXT='.exe'"])
        return args

    def _autotools_bool_arg(self, arg_base_name, value):
        prefix = "--enable-" if value else "--disable-"

        return prefix + arg_base_name

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"), r"-install_name \$rpath/", "-install_name ")

        if self.settings.compiler == "Visual Studio":
            self._build_visual()
        else:
            self._build_autotools()

    def _package_unix(self):
        self.copy("*sqlite3.h", src="install")
        self.copy("*.so*", dst="lib", src="install", keep_path=False, symlinks=True)
        self.copy("*.a", dst="lib", src="install", keep_path=False)
        self.copy("*.lib", dst="lib", src="install", keep_path=False)
        self.copy("*.dll", dst="bin", src="install", keep_path=False)
        self.copy("*.dylib", dst="lib", src="install", keep_path=False)
        self.copy("*LICENSE", dst="licenses", keep_path=False)

    def _package_visual(self):
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*LICENSE", dst="licenses", keep_path=False)
        self.copy("sqlite3.h", src=self._source_subfolder, dst=os.path.join("include", "sqlcipher"))

    def package(self):
        if self.settings.compiler == "Visual Studio":
            self._package_visual()
        else:
            self._package_unix()

    def package_info(self):
        self.cpp_info.libs = ["sqlcipher"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread", "dl"])
        self.cpp_info.defines = ["SQLITE_HAS_CODEC", 'SQLCIPHER_CRYPTO_OPENSSL', 'SQLITE_TEMP_STORE=2']
        # Allow using #include <sqlite3.h> even with sqlcipher (for libs like sqlpp11-connector-sqlite3)
        self.cpp_info.includedirs.append(os.path.join("include", "sqlcipher"))
