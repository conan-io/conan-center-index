from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os
import glob

required_conan_version = ">=1.43.0"


class LibpqConan(ConanFile):
    name = "libpq"
    description = "The library used by all the standard PostgreSQL tools."
    topics = ("libpq", "postgresql", "database", "db")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.postgresql.org/docs/current/static/libpq.html"
    license = "PostgreSQL"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
        "disable_rpath": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": False,
        "disable_rpath": False,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _is_clang8_x86(self):
        return self.settings.os == "Linux" and \
               self.settings.compiler == "clang" and \
               self.settings.compiler.version == "8" and \
               self.settings.arch == "x86"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.disable_rpath

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")

    def validate(self):
        if self.settings.os == "Windows" and self.settings.compiler == "gcc" and self.options.shared:
            raise ConanInvalidConfiguration("static mingw build is not possible")

    def build_requirements(self):
        if self._is_msvc:
            self.build_requires("strawberryperl/5.30.0.1")
        elif self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            args = ['--without-readline']
            args.append('--without-zlib')
            args.append('--with-openssl' if self.options.with_openssl else '--without-openssl')
            if tools.build.cross_building(self, self) and not self.options.with_openssl:
                args.append("--disable-strong-random")
            if tools.build.cross_building(self, self, skip_x64_x86=True):
                args.append("USE_DEV_URANDOM=1")
            if self.settings.os != "Windows" and self.options.disable_rpath:
                args.append('--disable-rpath')
            if self._is_clang8_x86:
                self._autotools.flags.append("-msse2")
            with tools.files.chdir(self, self._source_subfolder):
                self._autotools.configure(args=args)
        return self._autotools

    @property
    def _make_args(self):
        args = []
        if self.settings.os == "Windows":
            args.append("MAKE_DLL={}".format(str(self.options.shared).lower()))
        return args

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        if self._is_msvc:
            # https://www.postgresql.org/docs/8.3/install-win32-libpq.html
            # https://github.com/postgres/postgres/blob/master/src/tools/msvc/README
            if not self.options.shared:
                tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "src", "tools", "msvc", "MKvcbuild.pm"),
                                      "$libpq = $solution->AddProject('libpq', 'dll', 'interfaces',",
                                      "$libpq = $solution->AddProject('libpq', 'lib', 'interfaces',")
            system_libs = ", ".join(["'{}.lib'".format(lib) for lib in self.deps_cpp_info.system_libs])
            tools.files.replace_in_file(self, os.path.join(self._source_subfolder, "src", "tools", "msvc", "Project.pm"),
                                  "libraries             => [],",
                                  "libraries             => [{}],".format(system_libs))
            if self.settings.compiler == "Visual Studio":
                runtime = {
                    "MT": "MultiThreaded",
                    "MTd": "MultiThreadedDebug",
                    "MD": "MultiThreadedDLL",
                    "MDd": "MultiThreadedDebugDLL",
                }.get(str(self.settings.compiler.runtime))
            else:
                runtime = "MultiThreaded{}{}".format(
                    "Debug" if self.settings.compiler.runtime_type == "Debug" else "",
                    "DLL" if self.settings.compiler.runtime == "dynamic" else "",
                )
            msbuild_project_pm = os.path.join(self._source_subfolder, "src", "tools", "msvc", "MSBuildProject.pm")
            tools.files.replace_in_file(self, msbuild_project_pm, "</Link>", """</Link>
    <Lib>
      <TargetMachine>$targetmachine</TargetMachine>
    </Lib>""")
            tools.files.replace_in_file(self, msbuild_project_pm, "'MultiThreadedDebugDLL'", "'%s'" % runtime)
            tools.files.replace_in_file(self, msbuild_project_pm, "'MultiThreadedDLL'", "'%s'" % runtime)
            config_default_pl = os.path.join(self._source_subfolder, "src", "tools", "msvc", "config_default.pl")
            solution_pm = os.path.join(self._source_subfolder, "src", "tools", "msvc", "Solution.pm")
            if self.options.with_openssl:
                for ssl in ["VC\libssl32", "VC\libssl64", "libssl"]:
                    tools.files.replace_in_file(self, solution_pm,
                                          "%s.lib" % ssl,
                                          "%s.lib" % self.deps_cpp_info["openssl"].libs[0])
                for crypto in ["VC\libcrypto32", "VC\libcrypto64", "libcrypto"]:
                    tools.files.replace_in_file(self, solution_pm,
                                          "%s.lib" % crypto,
                                          "%s.lib" % self.deps_cpp_info["openssl"].libs[1])
                tools.files.replace_in_file(self, config_default_pl,
                                      "openssl   => undef",
                                      "openssl   => '%s'" % self.deps_cpp_info["openssl"].rootpath.replace("\\", "/"))
            with tools.vcvars(self.settings):
                config = "DEBUG" if self.settings.build_type == "Debug" else "RELEASE"
                with tools.environment_append({"CONFIG": config}):
                    with tools.files.chdir(self, os.path.join(self._source_subfolder, "src", "tools", "msvc")):
                        self.run("perl build.pl libpq")
                        if not self.options.shared:
                            self.run("perl build.pl libpgport")
        else:
            # relocatable shared lib on macOS
            tools.files.replace_in_file(self, 
                os.path.join(self._source_subfolder, "src", "Makefile.shlib"),
                "-install_name '$(libdir)/",
                "-install_name '@rpath/",
            )
            # avoid SIP issues on macOS when dependencies are shared
            if tools.is_apple_os(self, self.settings.os):
                libpaths = ":".join(self.deps_cpp_info.lib_paths)
                tools.files.replace_in_file(self, 
                    os.path.join(self._source_subfolder, "configure"),
                    "#! /bin/sh\n",
                    "#! /bin/sh\nexport DYLD_LIBRARY_PATH={}:$DYLD_LIBRARY_PATH\n".format(libpaths),
                )
            autotools = self._configure_autotools()
            with tools.files.chdir(self, os.path.join(self._source_subfolder, "src", "backend")):
                autotools.make(args=self._make_args, target="generated-headers")
            with tools.files.chdir(self, os.path.join(self._source_subfolder, "src", "common")):
                autotools.make(args=self._make_args)
            if tools.scm.Version(self, self.version) >= "12":
                with tools.files.chdir(self, os.path.join(self._source_subfolder, "src", "port")):
                    autotools.make(args=self._make_args)
            with tools.files.chdir(self, os.path.join(self._source_subfolder, "src", "include")):
                autotools.make(args=self._make_args)
            with tools.files.chdir(self, os.path.join(self._source_subfolder, "src", "interfaces", "libpq")):
                autotools.make(args=self._make_args)
            with tools.files.chdir(self, os.path.join(self._source_subfolder, "src", "bin", "pg_config")):
                autotools.make(args=self._make_args)

    def _remove_unused_libraries_from_package(self):
        if self.options.shared:
            if self.settings.os == "Windows":
                globs = []
            else:
                globs = [os.path.join(self.package_folder, "lib", "*.a")]
        else:
            globs = [
                os.path.join(self.package_folder, "lib", "libpq.so*"),
                os.path.join(self.package_folder, "bin", "*.dll"),
                os.path.join(self.package_folder, "lib", "libpq*.dylib")
            ]
        if self.settings.os == "Windows":
            os.unlink(os.path.join(self.package_folder, "lib", "libpq.dll"))
        for globi in globs:
            for file in glob.glob(globi):
                os.remove(file)

    def package(self):
        self.copy(pattern="COPYRIGHT", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            self.copy("*postgres_ext.h", src=self._source_subfolder, dst="include", keep_path=False)
            self.copy("*pg_config.h", src=self._source_subfolder, dst="include", keep_path=False)
            self.copy("*pg_config_ext.h", src=self._source_subfolder, dst="include", keep_path=False)
            self.copy("*libpq-fe.h", src=self._source_subfolder, dst="include", keep_path=False)
            self.copy("*libpq-events.h", src=self._source_subfolder, dst="include", keep_path=False)
            self.copy("*.h", src=os.path.join(self._source_subfolder, "src", "include", "libpq"), dst=os.path.join("include", "libpq"), keep_path=False)
            self.copy("*genbki.h", src=self._source_subfolder, dst=os.path.join("include", "catalog"), keep_path=False)
            self.copy("*pg_type.h", src=self._source_subfolder, dst=os.path.join("include", "catalog"), keep_path=False)
            if self.options.shared:
                self.copy("**/libpq.dll", src=self._source_subfolder, dst="bin", keep_path=False)
                self.copy("**/libpq.lib", src=self._source_subfolder, dst="lib", keep_path=False)
            else:
                self.copy("*.lib", src=self._source_subfolder, dst="lib", keep_path=False)
        else:
            autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)#self._configure_autotools()
            with tools.files.chdir(self, os.path.join(self._source_subfolder, "src", "common")):
                autotools.install(args=self._make_args)
            with tools.files.chdir(self, os.path.join(self._source_subfolder, "src", "include")):
                autotools.install(args=self._make_args)
            with tools.files.chdir(self, os.path.join(self._source_subfolder, "src", "interfaces", "libpq")):
                autotools.install(args=self._make_args)
            if tools.scm.Version(self, self.version) >= "12":
                with tools.files.chdir(self, os.path.join(self._source_subfolder, "src", "port")):
                    autotools.install(args=self._make_args)

            with tools.files.chdir(self, os.path.join(self._source_subfolder, "src", "bin", "pg_config")):
                autotools.install(args=self._make_args)

            self._remove_unused_libraries_from_package()

            tools.files.rmdir(self, os.path.join(self.package_folder, "include", "postgresql", "server"))
            self.copy(pattern="*.h", dst=os.path.join("include", "catalog"), src=os.path.join(self._source_subfolder, "src", "include", "catalog"))
        self.copy(pattern="*.h", dst=os.path.join("include", "catalog"), src=os.path.join(self._source_subfolder, "src", "backend", "catalog"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def _construct_library_name(self, name):
        if self._is_msvc:
            return "lib{}".format(name)
        return  name

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "PostgreSQL")
        self.cpp_info.set_property("cmake_target_name", "PostgreSQL::PostgreSQL")
        self.cpp_info.set_property("pkg_config_name", "libpq")

        self.cpp_info.names["cmake_find_package"] = "PostgreSQL"
        self.cpp_info.names["cmake_find_package_multi"] = "PostgreSQL"

        self.env_info.PostgreSQL_ROOT = self.package_folder

        self.cpp_info.components["pq"].libs = [self._construct_library_name("pq")]

        if self.options.with_openssl:
            self.cpp_info.components["pq"].requires.append("openssl::openssl")

        if not self.options.shared:
            if self._is_msvc:
                if tools.scm.Version(self, self.version) < "12":
                    self.cpp_info.components["pgport"].libs = ["libpgport"]
                    self.cpp_info.components["pq"].requires.extend(["pgport"])
                else:
                    self.cpp_info.components["pgcommon"].libs = ["libpgcommon"]
                    self.cpp_info.components["pgport"].libs = ["libpgport"]
                    self.cpp_info.components["pq"].requires.extend(["pgport", "pgcommon"])
            else:
                if tools.scm.Version(self, self.version) < "12":
                    self.cpp_info.components["pgcommon"].libs = ["pgcommon"]
                    self.cpp_info.components["pq"].requires.extend(["pgcommon"])
                else:
                    self.cpp_info.components["pgcommon"].libs = ["pgcommon", "pgcommon_shlib"]
                    self.cpp_info.components["pgport"].libs = ["pgport", "pgport_shlib"]
                    self.cpp_info.components["pq"].requires.extend(["pgport", "pgcommon"])

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["pq"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["pq"].system_libs = ["ws2_32", "secur32", "advapi32", "shell32", "crypt32", "wldap32"]
