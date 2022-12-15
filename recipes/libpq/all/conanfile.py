from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path, VCVars
from conan.tools.files import replace_in_file, rmdir
from conan.tools.scm import Version
import os
import glob

required_conan_version = ">=1.53.0"


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
    def _is_clang8_x86(self):
        return self.settings.os == "Linux" and \
               self.settings.compiler == "clang" and \
               self.settings.compiler.version == "8" and \
               self.settings.arch == "x86"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _make_args(self):
        args = []
        if self.settings.os == "Windows":
            args.append("MAKE_DLL={}".format(str(self.options.shared).lower()))
        return args

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe('fPIC')
            self.options.rm_safe('disable_rpath')

    def configure(self):
        if self.options.shared:
            self.options.rm_safe('fPIC')
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1q")

    def validate(self):
        if self.settings.os == "Windows" and self.settings.compiler == "gcc" and self.options.shared:
            raise ConanInvalidConfiguration("shared mingw build is not possible")

    def build_requirements(self):
        if is_msvc(self):
            self.tool_requires("strawberryperl/5.32.1.1")
        elif self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        if is_msvc(self):
            vcvars = VCVars(self)
            vcvars.generate()
        else:
            if not cross_building(self):
                env = VirtualRunEnv(self)
                env.generate(scope="build")
            tc = AutotoolsToolchain(self)
            tc.configure_args.append('--without-readline')
            tc.configure_args.append('--without-zlib')
            tc.configure_args.append('--with-openssl' if self.options.with_openssl else '--without-openssl')
            if cross_building(self) and not self.options.with_openssl:
                tc.configure_args.append("--disable-strong-random")
            if cross_building(self, skip_x64_x86=True):
                tc.configure_args.append("USE_DEV_URANDOM=1")
            if self.settings.os != "Windows" and self.options.disable_rpath:
                tc.configure_args.append('--disable-rpath')
            if self._is_clang8_x86:
                tc.extra_cflags.append("-msse2")
            tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        if is_msvc(self):
            # https://www.postgresql.org/docs/8.3/install-win32-libpq.html
            # https://github.com/postgres/postgres/blob/master/src/tools/msvc/README
            if not self.options.shared:
                replace_in_file(self,os.path.join(self.source_folder, "src", "tools", "msvc", "MKvcbuild.pm"),
                                      "$libpq = $solution->AddProject('libpq', 'dll', 'interfaces',",
                                      "$libpq = $solution->AddProject('libpq', 'lib', 'interfaces',")
            system_libs = ", ".join(["'{}.lib'".format(lib) for lib in self.deps_cpp_info.system_libs])
            replace_in_file(self,os.path.join(self.source_folder, "src", "tools", "msvc", "Project.pm"),
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
            msbuild_project_pm = os.path.join(self.source_folder, "src", "tools", "msvc", "MSBuildProject.pm")
            replace_in_file(self,msbuild_project_pm, "</Link>", """</Link>
    <Lib>
      <TargetMachine>$targetmachine</TargetMachine>
    </Lib>""")
            replace_in_file(self,msbuild_project_pm, "'MultiThreadedDebugDLL'", "'%s'" % runtime)
            replace_in_file(self,msbuild_project_pm, "'MultiThreadedDLL'", "'%s'" % runtime)
            config_default_pl = os.path.join(self.source_folder, "src", "tools", "msvc", "config_default.pl")
            solution_pm = os.path.join(self.source_folder, "src", "tools", "msvc", "Solution.pm")
            if self.options.with_openssl:
                for ssl in ["VC\libssl32", "VC\libssl64", "libssl"]:
                    replace_in_file(self,solution_pm,
                                          "%s.lib" % ssl,
                                          "%s.lib" % self.deps_cpp_info["openssl"].libs[0])
                for crypto in ["VC\libcrypto32", "VC\libcrypto64", "libcrypto"]:
                    replace_in_file(self,solution_pm,
                                          "%s.lib" % crypto,
                                          "%s.lib" % self.deps_cpp_info["openssl"].libs[1])
                replace_in_file(self,config_default_pl,
                                      "openssl   => undef",
                                      "openssl   => '%s'" % self.deps_cpp_info["openssl"].rootpath.replace("\\", "/"))

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            config = "DEBUG" if self.settings.build_type == "Debug" else "RELEASE"
            build_env = VirtualRunEnv(self)
            env = build_env.environment()
            env.define("CONFIG", config)
            build_env.generate()

            dir = os.path.join(self.source_folder, "src", "tools", "msvc")
            self.run("perl build.pl libpq", cwd=dir)
            if not self.options.shared:
                self.run("perl build.pl libpgport", cwd=dir)
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

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
        self.copy(pattern="COPYRIGHT", dst="licenses", src=self.source_folder)
        if is_msvc(self):
            self.copy("*postgres_ext.h", src=self.source_folder, dst="include", keep_path=False)
            self.copy("*pg_config.h", src=self.source_folder, dst="include", keep_path=False)
            self.copy("*pg_config_ext.h", src=self.source_folder, dst="include", keep_path=False)
            self.copy("*libpq-fe.h", src=self.source_folder, dst="include", keep_path=False)
            self.copy("*libpq-events.h", src=self.source_folder, dst="include", keep_path=False)
            self.copy("*.h", src=os.path.join(self.source_folder, "src", "include", "libpq"), dst=os.path.join("include", "libpq"), keep_path=False)
            self.copy("*genbki.h", src=self.source_folder, dst=os.path.join("include", "catalog"), keep_path=False)
            self.copy("*pg_type.h", src=self.source_folder, dst=os.path.join("include", "catalog"), keep_path=False)
            if self.options.shared:
                self.copy("**/libpq.dll", src=self.source_folder, dst="bin", keep_path=False)
                self.copy("**/libpq.lib", src=self.source_folder, dst="lib", keep_path=False)
            else:
                self.copy("*.lib", src=self.source_folder, dst="lib", keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
            self._remove_unused_libraries_from_package()

            rmdir(self, os.path.join(self.package_folder, "include", "postgresql", "server"))
            self.copy(pattern="*.h", dst=os.path.join("include", "catalog"), src=os.path.join(self.source_folder, "src", "include", "catalog"))
        self.copy(pattern="*.h", dst=os.path.join("include", "catalog"), src=os.path.join(self.source_folder, "src", "backend", "catalog"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def _construct_library_name(self, name):
        if is_msvc(self):
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
            if is_msvc(self):
                if self.version < "12":
                    self.cpp_info.components["pgport"].libs = ["libpgport"]
                    self.cpp_info.components["pq"].requires.extend(["pgport"])
                else:
                    self.cpp_info.components["pgcommon"].libs = ["libpgcommon"]
                    self.cpp_info.components["pgport"].libs = ["libpgport"]
                    self.cpp_info.components["pq"].requires.extend(["pgport", "pgcommon"])
            else:
                if Version(self.version) < "12":
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
