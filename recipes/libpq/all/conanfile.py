from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, unix_path, VCVars
from conan.tools.scm import Version
import glob
import os

required_conan_version = ">=1.54.0"


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
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
            self.options.rm_safe("disable_rpath")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1s")

    def build_requirements(self):
        if is_msvc(self):
            self.tool_requires("strawberryperl/5.32.1.1")
        elif self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if is_msvc(self):
            vcvars = VCVars(self)
            vcvars.generate()
            config = "DEBUG" if self.settings.build_type == "Debug" else "RELEASE"
            env = Environment()
            env.define("CONFIG", config)
            env.vars(self).save_script("conanbuild_msvc")
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
            tc.make_args.append(f"DESTDIR={unix_path(self, self.package_folder)}")
            if self.settings.os == "Windows":
                tc.make_args.append("MAKE_DLL={}".format(str(self.options.shared).lower()))
            tc.generate()
            AutotoolsDeps(self).generate()

    def _patch_sources(self):
        if is_msvc(self):
            # https://www.postgresql.org/docs/8.3/install-win32-libpq.html
            # https://github.com/postgres/postgres/blob/master/src/tools/msvc/README
            if not self.options.shared:
                replace_in_file(self,os.path.join(self.source_folder, "src", "tools", "msvc", "MKvcbuild.pm"),
                                      "$libpq = $solution->AddProject('libpq', 'dll', 'interfaces',",
                                      "$libpq = $solution->AddProject('libpq', 'lib', 'interfaces',")
            host_deps = [dep for _, dep in self.dependencies.host.items()]
            system_libs = []
            for dep in host_deps:
                system_libs.extend(dep.cpp_info.aggregated_components().system_libs)
        
            linked_system_libs = ", ".join(["'{}.lib'".format(lib) for lib in system_libs])
            replace_in_file(self,os.path.join(self.source_folder, "src", "tools", "msvc", "Project.pm"),
                                  "libraries             => [],",
                                  "libraries             => [{}],".format(linked_system_libs))
            runtime = {
                "MT": "MultiThreaded",
                "MTd": "MultiThreadedDebug",
                "MD": "MultiThreadedDLL",
                "MDd": "MultiThreadedDebugDLL",
            }.get(msvc_runtime_flag(self))
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
                openssl = self.dependencies["openssl"]
                for ssl in ["VC\\libssl32", "VC\\libssl64", "libssl"]:
                    replace_in_file(self,solution_pm,
                                          "%s.lib" % ssl,
                                          "%s.lib" % openssl.cpp_info.components["ssl"].libs[0])
                for crypto in ["VC\\libcrypto32", "VC\\libcrypto64", "libcrypto"]:
                    replace_in_file(self,solution_pm,
                                          "%s.lib" % crypto,
                                          "%s.lib" % openssl.cpp_info.components["crypto"].libs[0])
                replace_in_file(self,config_default_pl,
                                      "openssl   => undef",
                                      "openssl   => '%s'" % openssl.package_folder.replace("\\", "/"))
        elif self.settings.os == "Windows":
            if self.settings.get_safe("compiler.threads") == "posix":
                # Use MinGW pthread library
                replace_in_file(self, os.path.join(self.source_folder, "src", "interfaces", "libpq", "Makefile"),
                "ifeq ($(enable_thread_safety), yes)\nOBJS += pthread-win32.o\nendif",
                "")

    def build(self):
        apply_conandata_patches(self)
        self._patch_sources()
        if is_msvc(self):
            with chdir(self, os.path.join(self.source_folder, "src", "tools", "msvc")):
                self.run("perl build.pl libpq")
                if not self.options.shared:
                    self.run("perl build.pl libpgport")
        else:
            autotools = Autotools(self)
            with chdir(self, os.path.join(self.source_folder)):
                autotools.configure()
            with chdir(self, os.path.join(self.source_folder, "src", "backend")):
                autotools.make(target="generated-headers")
            with chdir(self, os.path.join(self.source_folder, "src", "common")):
                autotools.make()
            with chdir(self, os.path.join(self.source_folder, "src", "include")):
                autotools.make()
            with chdir(self, os.path.join(self.source_folder, "src", "interfaces", "libpq")):
                autotools.make()
            if Version(self.version) >= 12:
                with chdir(self, os.path.join(self.source_folder, "src", "port")):
                    autotools.make()
            with chdir(self, os.path.join(self.source_folder, "src", "bin", "pg_config")):
                autotools.make()

    def _remove_unused_libraries_from_package(self):
        bin_folder = os.path.join(self.package_folder, "bin")
        lib_folder = os.path.join(self.package_folder, "lib")
        rm(self, "*.dll", lib_folder)
        if self.options.shared:
            for lib in glob.glob(os.path.join(lib_folder, "*.a")):
                if not (self.settings.os == "Windows" and os.path.basename(lib) == "libpq.dll.a"):
                    os.remove(lib)
        else:
            rm(self, "*.dll", bin_folder)
            rm(self, "*.dll.a", lib_folder)
            rm(self, "*.so*", lib_folder)
            rm(self, "*.dylib", lib_folder)

    def package(self):
        copy(self, "COPYRIGHT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self, pattern="*postgres_ext.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder, keep_path=False)
            copy(self, pattern="*pg_config.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder, keep_path=False)
            copy(self, pattern="*pg_config_ext.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder, keep_path=False)
            copy(self, pattern="*libpq-fe.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder, keep_path=False)
            copy(self, pattern="*libpq-events.h", dst=os.path.join(self.package_folder, "include"), src=self.source_folder, keep_path=False)
            copy(self, pattern="*.h", src=os.path.join(self.source_folder, "src", "include", "libpq"),
                                      dst=os.path.join(self.package_folder, "include", "libpq"),
                                      keep_path=False)
            copy(self, pattern="*genbki.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include", "catalog"), keep_path=False)
            copy(self, pattern="*pg_type.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include", "catalog"), keep_path=False)
            if self.options.shared:
                copy(self, pattern="**/libpq.dll", dst=os.path.join(self.package_folder, "bin"), src=self.source_folder, keep_path=False)
                copy(self, pattern="**/libpq.lib", dst=os.path.join(self.package_folder, "lib"), src=self.source_folder, keep_path=False)
            else:
                copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.source_folder, keep_path=False)
        else:
            autotools = Autotools(self)
            with chdir(self, os.path.join(self.source_folder, "src", "common")):
                autotools.install()
            with chdir(self, os.path.join(self.source_folder, "src", "include")):
                autotools.install()
            with chdir(self, os.path.join(self.source_folder, "src", "interfaces", "libpq")):
                autotools.install()
            if Version(self.version) >= 12:
                with chdir(self, os.path.join(self.source_folder, "src", "port")):
                    autotools.install()
            with chdir(self, os.path.join(self.source_folder, "src", "bin", "pg_config")):
                autotools.install()
            copy(self, "*.h", src=os.path.join(self.build_folder, "src", "include", "catalog"),
                              dst=os.path.join(self.package_folder, "include", "catalog"))
            rmdir(self, os.path.join(self.package_folder, "share"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "include", "postgresql", "server"))
            self._remove_unused_libraries_from_package()
            fix_apple_shared_install_name(self)
        copy(self, "*.h", src=os.path.join(self.build_folder, "src", "backend", "catalog"),
                          dst=os.path.join(self.package_folder, "include", "catalog"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "PostgreSQL")
        self.cpp_info.set_property("cmake_target_name", "PostgreSQL::PostgreSQL")
        self.cpp_info.set_property("pkg_config_name", "libpq")

        self.env_info.PostgreSQL_ROOT = self.package_folder

        self.cpp_info.components["pq"].libs = [f"{'lib' if is_msvc(self) else ''}pq"]

        if self.options.with_openssl:
            self.cpp_info.components["pq"].requires.append("openssl::openssl")

        if not self.options.shared:
            if is_msvc(self):
                self.cpp_info.components["pgport"].libs = ["libpgport"]
                self.cpp_info.components["pq"].requires.append("pgport")
                if Version(self.version) >= "12":
                    self.cpp_info.components["pgcommon"].libs = ["libpgcommon"]
                    self.cpp_info.components["pq"].requires.append("pgcommon")
            else:
                self.cpp_info.components["pgcommon"].libs = ["pgcommon"]
                self.cpp_info.components["pq"].requires.append("pgcommon")
                if Version(self.version) >= "12":
                    self.cpp_info.components["pgcommon"].libs.append("pgcommon_shlib")
                    self.cpp_info.components["pgport"].libs = ["pgport", "pgport_shlib"]
                    if self.settings.os == "Windows":
                        self.cpp_info.components["pgport"].system_libs = ["ws2_32"]
                    self.cpp_info.components["pgcommon"].requires.append("pgport")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["pq"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["pq"].system_libs = ["ws2_32", "secur32", "advapi32", "shell32", "crypt32", "wldap32"]

        self.cpp_info.names["cmake_find_package"] = "PostgreSQL"
        self.cpp_info.names["cmake_find_package_multi"] = "PostgreSQL"
