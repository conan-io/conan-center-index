import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import VCVars, is_msvc, is_msvc_static_runtime, NMakeToolchain, NMakeDeps
from conan.tools.scm import Version

required_conan_version = ">=1.58.0"


class SqlcipherConan(ConanFile):
    name = "sqlcipher"
    description = "SQLite extension that provides 256 bit AES encryption of database files."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.zetetic.net/sqlcipher/"
    topics = ("database", "encryption", "sqlite")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "crypto_library": ["openssl", "libressl", "commoncrypto"],
        "with_largefile": [True, False],
        "temporary_store": ["always_file", "default_file", "default_memory", "always_memory"],
        "enable_column_metadata": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "crypto_library": "openssl",
        "with_largefile": True,
        "temporary_store": "default_memory",
        "enable_column_metadata": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            self.options.rm_safe("with_largefile")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.crypto_library == "openssl":
            self.requires("openssl/[>=1.1 <4]")
        elif self.options.crypto_library == "libressl":
            self.requires("libressl/3.5.3")

    def validate(self):
        if self.options.crypto_library == "commoncrypto" and not is_apple_os(self):
            raise ConanInvalidConfiguration("commoncrypto is only supported on Macos")

    def build_requirements(self):
        self.tool_requires("tcl/8.6.13")
        if not is_msvc(self):
            self.tool_requires("gnu-config/cci.20210814")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)


    @property
    def _temp_store_nmake_value(self):
        return {
            "always_file": "0",
            "default_file": "1",
            "default_memory": "2",
            "always_memory": "3",
        }.get(str(self.options.temporary_store))

    @property
    def _temp_store_autotools_value(self):
        return {
            "always_file": "never",
            "default_file": "no",
            "default_memory": "yes",
            "always_memory": "always",
        }.get(str(self.options.temporary_store))

    def _generate_msvc(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = NMakeToolchain(self)
        env = tc.environment()
        crypto_dep = self.dependencies[str(self.options.crypto_library)].cpp_info
        env.define("TLIBS", " ".join(lib + ".lib" for lib in crypto_dep.libs + crypto_dep.system_libs))
        env.define("LTLIBPATHS", f"/LIBPATH:{crypto_dep.libdir}")
        env.define("OPTS", f'-I{crypto_dep.includedir} -DSQLITE_HAS_CODEC')
        env.define("NO_TCL", "1")
        env.define("USE_AMALGAMATION", "1")
        opt_feature_flags = "-DSQLCIPHER_CRYPTO_OPENSSL"
        if self.options.enable_column_metadata:
            opt_feature_flags += " -DSQLITE_ENABLE_COLUMN_METADATA"
        env.define("OPT_FEATURE_FLAGS", opt_feature_flags)
        env.define("SQLITE_TEMP_STORE", self._temp_store_nmake_value)
        env.define("TCLSH_CMD", self.dependencies.build['tcl'].runenv_info.vars(self)['TCLSH'])

        if not is_msvc_static_runtime(self):
            env.define("USE_CRT_DLL", "1")
        if self.settings.build_type == "Debug":
            env.define("DEBUG", "2")
        env.define("FOR_WIN10", "1")
        env.define("PLATFORM", {"x86": "x86", "x86_64": "x64"}[str(self.settings.arch)])
        tc.generate(env)

        tc = NMakeDeps(self)
        tc.generate()

        vcvars = VCVars(self)
        vcvars.generate()

    @property
    def _use_commoncrypto(self):
        return self.options.crypto_library == "commoncrypto" and is_apple_os(self)

    def _generate_unix(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = AutotoolsToolchain(self)
        tc.configure_args += [
            f"--enable-tempstore={self._temp_store_autotools_value}",
            "--disable-tcl",
        ]
        if self.settings.os == "Windows":
            tc.configure_args += [
                "config_BUILD_EXEEXT='.exe'",
                "config_TARGET_EXEEXT='.exe'",
            ]

        if self.settings.os in ["Linux", "FreeBSD"]:
            tc.extra_ldflags.append("-ldl")
            if not self.options.with_largefile:
                tc.extra_defines.append("SQLITE_DISABLE_LFS=1")
        tc.extra_defines.append("SQLITE_HAS_CODEC")

        if self._use_commoncrypto:
            tc.extra_ldflags += [
                "-framework", "Security",
                "-framework", "CoreFoundation",
            ]
            tc.configure_args.append("--with-crypto-lib=commoncrypto")
        else:
            tc.extra_defines.append("SQLCIPHER_CRYPTO_OPENSSL")
        tc.generate()

        deps = AutotoolsDeps(self)
        deps.generate()

    def generate(self):
        if is_msvc(self):
            self._generate_msvc()
        else:
            self._generate_unix()

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix":
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def _patch_sources_unix(self):
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str),
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config), os.path.dirname(gnu_config), os.path.join(self.source_folder, "build-aux"))
        configure = os.path.join(self.source_folder, "configure")
        self._chmod_plus_x(configure)
        # relocatable shared libs on macOS
        replace_in_file(self, configure, "-install_name \\$rpath/", "-install_name @rpath/")
        # avoid SIP issues on macOS when dependencies are shared
        if is_apple_os(self):
            libdirs = sum([dep.cpp_info.libdirs for dep in self.dependencies.values()], [])
            libpaths = ":".join(libdirs)
            replace_in_file(self, configure,
                            "#! /bin/sh\n",
                            f"#! /bin/sh\nexport DYLD_LIBRARY_PATH={libpaths}:$DYLD_LIBRARY_PATH\n")

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            with chdir(self, self.source_folder):
                main_target = "dll" if self.options.shared else "sqlcipher.lib"
                self.run(f"nmake /f Makefile.msc {main_target}")
        else:
            self._patch_sources_unix()
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.configure()
                if self.settings.os == "Windows":
                    # sqlcipher will create .exe for the build machine, which we defined to Linux...
                    replace_in_file(self, "Makefile", "BEXE = .exe", "BEXE = ")
                autotools.make()

    def package(self):
        copy(self, "LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if is_msvc(self):
            copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=self.source_folder, keep_path=False)
            copy(self, "*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.source_folder, keep_path=False)
            copy(self, "sqlite3.h", dst=os.path.join(self.package_folder, "include", "sqlcipher"), src=self.source_folder)
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.install()
            rm(self, "*.la", self.package_folder, recursive=True)
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "sqlcipher")
        self.cpp_info.libs = ["sqlcipher"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "dl"])
            if Version(self.version) >= "4.5.0":
                self.cpp_info.system_libs.append("m")
        self.cpp_info.defines = [
            "SQLITE_HAS_CODEC",
            f"SQLITE_TEMP_STORE={self._temp_store_nmake_value}"
        ]
        if self._use_commoncrypto:
            self.cpp_info.frameworks = ["Security", "CoreFoundation"]
        else:
            self.cpp_info.defines.append("SQLCIPHER_CRYPTO_OPENSSL")
        # Allow using #include <sqlite3.h> even with sqlcipher (for libs like sqlpp11-connector-sqlite3)
        self.cpp_info.includedirs.append(os.path.join("include", "sqlcipher"))
