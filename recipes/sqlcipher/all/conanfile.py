from conan.tools.microsoft import msvc_runtime_flag
from conans import tools, ConanFile, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import functools
import os
import shutil

required_conan_version = ">=1.36.0"


class SqlcipherConan(ConanFile):
    name = "sqlcipher"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.zetetic.net/sqlcipher/"
    description = "SQLite extension that provides 256 bit AES encryption of database files."
    topics = ("database", "encryption", "SQLite")

    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "crypto_library": ["openssl", "libressl", "commoncrypto"],
        "with_largefile": [True, False],
        "temporary_store": ["always_file", "default_file", "default_memory", "always_memory"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "crypto_library": "openssl",
        "with_largefile": True,
        "temporary_store": "default_memory",
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.with_largefile

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.crypto_library == "openssl":
            self.requires("openssl/1.1.1n")
        elif self.options.crypto_library == "libressl":
            self.requires("libressl/3.4.3")

    def validate(self):
        if self.options.crypto_library == "commoncrypto" and not tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("commoncrypto is only supported on Macos")

    def build_requirements(self):
        self.build_requires("tcl/8.6.11")
        if not self._is_msvc:
            self.build_requires("gnu-config/cci.20201022")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

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

        if msvc_runtime_flag(self) in ["MD", "MDd"]:
            nmake_flags.append("USE_CRT_DLL=1")
        if self.settings.build_type == "Debug":
            nmake_flags.append("DEBUG=2")
        nmake_flags.append("FOR_WIN10=1")
        platforms = {"x86": "x86", "x86_64": "x64"}
        nmake_flags.append("PLATFORM=%s" % platforms[str(self.settings.arch)])
        vcvars = tools.vcvars_command(self.settings)
        self.run("%s && nmake /f Makefile.msc %s %s" % (vcvars, main_target, " ".join(nmake_flags)), cwd=self._source_subfolder)

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def _build_autotools(self):
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config.guess"))
        configure = os.path.join(self._source_subfolder, "configure")
        self._chmod_plus_x(configure)
        # relocatable shared libs on macOS
        tools.replace_in_file(configure, "-install_name \\$rpath/", "-install_name @rpath/")
        # avoid SIP issues on macOS when dependencies are shared
        if tools.is_apple_os(self.settings.os):
            libpaths = ":".join(self.deps_cpp_info.lib_paths)
            tools.replace_in_file(
                configure,
                "#! /bin/sh\n",
                "#! /bin/sh\nexport DYLD_LIBRARY_PATH={}:$DYLD_LIBRARY_PATH\n".format(libpaths),
            )
        autotools = self._configure_autotools()
        autotools.make()

    @functools.lru_cache(1)
    def _configure_autotools(self):
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-tempstore={}".format(self._temp_store_autotools_value),
            "--disable-tcl",
        ]
        if self.settings.os == "Windows":
            args.extend(["config_BUILD_EXEEXT='.exe'", "config_TARGET_EXEEXT='.exe'"])

        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self.settings.os == "Linux":
            autotools.libs.append("dl")
            if not self.options.with_largefile:
                autotools.defines.append("SQLITE_DISABLE_LFS=1")
        autotools.defines.append("SQLITE_HAS_CODEC")

        env_vars = autotools.vars
        tclsh_cmd = self.deps_env_info.TCLSH
        env_vars["TCLSH_CMD"] = tclsh_cmd.replace("\\", "/")
        if self._use_commoncrypto():
            env_vars["LDFLAGS"] += " -framework Security -framework CoreFoundation "
            args.append("--with-crypto-lib=commoncrypto")
        else:
            autotools.defines.append("SQLCIPHER_CRYPTO_OPENSSL")

        autotools.configure(configure_dir=self._source_subfolder, args=args, vars=env_vars)
        if self.settings.os == "Windows":
            # sqlcipher will create .exe for the build machine, which we defined to Linux...
            tools.replace_in_file("Makefile", "BEXE = .exe", "BEXE = ")
        return autotools

    def _use_commoncrypto(self):
        return self.options.crypto_library == "commoncrypto" and tools.is_apple_os(self.settings.os)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self._is_msvc:
            self._build_visual()
        else:
            self._build_autotools()

    def _package_unix(self):
        autotools = self._configure_autotools()
        autotools.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def _package_visual(self):
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("sqlite3.h", src=self._source_subfolder, dst=os.path.join("include", "sqlcipher"))

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            self._package_visual()
        else:
            self._package_unix()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "sqlcipher")
        self.cpp_info.libs = ["sqlcipher"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl"])
            if tools.Version(self.version) >= "4.5.0":
                self.cpp_info.system_libs.append("m")
        self.cpp_info.defines = ["SQLITE_HAS_CODEC", "SQLITE_TEMP_STORE={}".format(self._temp_store_nmake_value)]
        if self._use_commoncrypto():
            self.cpp_info.frameworks = ["Security", "CoreFoundation"]
        else:
            self.cpp_info.defines.append("SQLCIPHER_CRYPTO_OPENSSL")
        # Allow using #include <sqlite3.h> even with sqlcipher (for libs like sqlpp11-connector-sqlite3)
        self.cpp_info.includedirs.append(os.path.join("include", "sqlcipher"))
