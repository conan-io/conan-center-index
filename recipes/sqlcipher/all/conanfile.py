from conans import tools, ConanFile, AutoToolsBuildEnvironment, RunEnvironment
from conans.errors import ConanInvalidConfiguration
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
    options = {
                "shared": [True, False],
                "fPIC": [True, False],
                "crypto_library": ["openssl", "libressl", "commoncrypto"],
                "with_largefile": [True, False],
                "temporary_store": ["always_file", "default_file", "default_memory", "always_memory"]
              }
    default_options = {
                        "shared": False,
                        "fPIC": True,
                        "crypto_library": "openssl",
                        "with_largefile": True,
                        "temporary_store": "default_memory"
                      }
    topics = ("database", "encryption", "SQLite")
    exports_sources = "patches/*"
    generators = "cmake"
    _source_subfolder = "source_subfolder"


    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os != "Linux":
            del self.options.with_largefile
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.crypto_library == "commoncrypto" and not tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("commoncrypto is only supported on Macos")
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        # It is possible to have a MinGW cross-build toolchain (Linux to Windows)
        # Only require msys2 when building on an actual Windows system
        if self.settings.os == "Windows" and self.settings.compiler == "gcc" and tools.os_info.is_windows:
            self.build_requires("msys2/20190524")
        self.build_requires("tcl/8.6.10")

    def requirements(self):
        if self.options.crypto_library == "openssl":
            self.requires("openssl/1.1.1k")
        elif self.options.crypto_library == "libressl":
            self.requires("libressl/3.2.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _temp_store_nmake_value(self):
        return {"always_file": "0",
                "default_file": "1",
                "default_memory": "2",
                "always_memory": "3"}.get(str(self.options.temporary_store))

    @property
    def _temp_store_autotools_value(self):
        return {"always_file": "never",
                "default_file": "no",
                "default_memory": "yes",
                "always_memory": "always"}.get(str(self.options.temporary_store))

    def _build_visual(self):
        crypto_dep = self.deps_cpp_info[str(self.options.crypto_library)]
        crypto_incdir = crypto_dep.include_paths[0]
        crypto_libdir = crypto_dep.lib_paths[0]
        libs = map(lambda lib : lib + ".lib", crypto_dep.libs)
        system_libs = map(lambda lib : lib + ".lib", crypto_dep.system_libs)

        nmake_flags = [
                "TLIBS=\"%s %s\"" % (" ".join(libs), " ".join(system_libs)),
                "LTLIBPATHS=/LIBPATH:%s" % crypto_libdir,
                "OPTS=\"-I%s -DSQLITE_HAS_CODEC\"" % (crypto_incdir),
                "NO_TCL=1",
                "USE_AMALGAMATION=1",
                "OPT_FEATURE_FLAGS=-DSQLCIPHER_CRYPTO_OPENSSL",
                "SQLITE_TEMP_STORE=%s" % self._temp_store_nmake_value,
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
            if not self.options.with_largefile:
                autotools_env.defines.append("SQLITE_DISABLE_LFS=1")
        autotools_env.defines.extend(["SQLITE_HAS_CODEC"])
        if not self._use_commoncrypto():
            autotools_env.defines.extend(["SQLCIPHER_CRYPTO_OPENSSL"])

        # sqlcipher config.sub does not contain android configurations...
        # elf is the most basic `os' for Android
        host = None
        if self.settings.os == "Android":
            host = "%s-linux-elf" % self._arch_id_str_compiler
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
            tclsh_cmd = self.deps_env_info.TCLSH
            env_vars["TCLSH_CMD"] = tclsh_cmd.replace("\\", "/")
            if self._use_commoncrypto():
                env_vars["LDFLAGS"] += " -framework Security -framework CoreFoundation "
            autotools_env.configure(args=configure_args, host=host, build=build, vars=env_vars)
            if self.settings.os == "Windows":
                # sqlcipher will create .exe for the build machine, which we defined to Linux...
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
            "--enable-tempstore=%s" % self._temp_store_autotools_value,
            "--disable-tcl",
        ]
        if self.settings.os == "Windows":
            args.extend(["config_BUILD_EXEEXT='.exe'", "config_TARGET_EXEEXT='.exe'"])
        if self._use_commoncrypto():
            args.extend(["--with-crypto-lib=commoncrypto"])
        return args

    def _autotools_bool_arg(self, arg_base_name, value):
        prefix = "--enable-" if value else "--disable-"

        return prefix + arg_base_name

    def _use_commoncrypto(self):
        return self.options.crypto_library == "commoncrypto" and tools.is_apple_os(self.settings.os)

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
        self.cpp_info.defines = ["SQLITE_HAS_CODEC", 'SQLITE_TEMP_STORE=%s' % self._temp_store_nmake_value]
        if self._use_commoncrypto():
            self.cpp_info.frameworks = ["Security", "CoreFoundation"]
        else:
            self.cpp_info.defines.extend(['SQLCIPHER_CRYPTO_OPENSSL'])
        # Allow using #include <sqlite3.h> even with sqlcipher (for libs like sqlpp11-connector-sqlite3)
        self.cpp_info.includedirs.append(os.path.join("include", "sqlcipher"))
