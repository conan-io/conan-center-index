import os
import re

from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


class AprConan(ConanFile):
    name = "apr"
    description = (
        "The Apache Portable Runtime (APR) provides a predictable and consistent "
        "interface to underlying platform-specific implementations"
    )
    license = "Apache-2.0"
    topics = ("apache", "platform", "library")
    homepage = "https://apr.apache.org/"
    url = "https://github.com/conan-io/conan-center-index"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "force_apr_uuid": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "force_apr_uuid": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _should_call_autoreconf(self):
        return self.settings.compiler == "apple-clang" and \
               Version(self.settings.compiler.version) >= "12" and \
               self.version == "1.7.0"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        if is_msvc(self):
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def validate_build(self):
        if cross_building(self) and not is_msvc(self):
            # Conan provide for Windows and Linux a simple "hack" to avoid entering a pre-built cached file
            if self.settings.os not in ("Windows", "Linux") and self.conf.get("user.apr:cache_file") is None:
                raise ConanInvalidConfiguration("apr recipe doesn't support cross-build for all the platforms"
                                                " due to runtime checks in autoconf. You can provide"
                                                " a cached file via Conan conf: \n"
                                                " [conf]\nuser.apr:cache_file=/path/to/cache_file to try it.")

    def build_requirements(self):
        if not is_msvc(self):
            if self._should_call_autoreconf:
                self.tool_requires("libtool/2.4.7")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _get_cross_building_configure_args(self):
        """
        The APR configure.in script makes extensive (30 instances) use
        Check warning on line 73 in recipes/apr/all/conanfile.py

        String statement has no effect of AC_TRY_RUN (to determine system capabilities) and
        checks for /dev/zero. These runtime checks only work when run on the host so
        the configure script will fail when cross compiling unless the relevant
        configuration variables are provided in a cache file or on the command line or in an
        environment variable. The configuration variable values are most easily determined by
        running the configure script on a host system using:

            ./configure --cache-file={gnu_host_triplet}.cache

        The generated cache file can be repeatedly used to cross-compile to the targeted host system
        by including it with the recipe data.

        This recipe is reading this custom user conf variable:

            [conf]
            user.apr:cache_file=/path/to/{gnu_host_triplet}.cache

        So you can use it to cross-compile on your system.
        """
        configure_args = []
        user_cache_file = self.conf.get("user.apr:cache_file", check_type=str)
        if user_cache_file:
            configure_args.append(f"--cache-file={user_cache_file}")
            return configure_args

        self.output.warning("Trying to set some configuration arguments, but it"
                            " could fail. The best approach is to provide a"
                            " pre-built cached file.")
        # Let's try this hack (tested on Linux ARM and Intel)
        if self.settings.os == "Linux":
            # The following are known to be true in modern Linux
            configure_args.extend(["apr_cv_mutex_robust_shared=yes",
                                   "ac_cv_file__dev_zero=yes",
                                   "ac_cv_mmap__dev_zero=yes",
                                   "ac_cv_define_PTHREAD_PROCESS_SHARED=yes",
                                   "apr_cv_process_shared_works=yes",
                                   "apr_cv_tcp_nodelay_with_cork=yes"])
        elif self.settings.os == "Windows":
            configure_args.extend(["apr_cv_mutex_robust_shared=no"
                                   "ac_cv_file__dev_zero=no",
                                   "ac_cv_mmap__dev_zero=no",
                                   "ac_cv_define_PTHREAD_PROCESS_SHARED=yes",
                                   "apr_cv_tcp_nodelay_with_cork=no"])
        return configure_args

    def generate(self):
        if is_msvc(self):
            tc = CMakeToolchain(self)
            tc.variables["INSTALL_PDB"] = False
            tc.variables["APR_BUILD_TESTAPR"] = False
            tc.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            tc = AutotoolsToolchain(self)
            tc.configure_args.append("--with-installbuilddir=${prefix}/res/build-1")
            if cross_building(self):
                tc.configure_args.extend(self._get_cross_building_configure_args())
            tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        if self.options.force_apr_uuid:
            replace_in_file(self, os.path.join(self.source_folder, "include", "apr.h.in"),
                                  "@osuuid@", "0")

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build(target="libapr-1" if self.options.shared else "apr-1")
        else:
            autotools = Autotools(self)
            if self._should_call_autoreconf:
                autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            cmake = CMake(self)
            cmake.install()
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "build-1"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            fix_apple_shared_install_name(self)

            apr_rules_mk = os.path.join(self.package_folder, "res", "build-1", "apr_rules.mk")
            apr_rules_cnt = open(apr_rules_mk).read()
            for key in ("apr_builddir", "apr_builders", "top_builddir"):
                apr_rules_cnt, nb = re.subn(f"^{key}=[^\n]*\n", f"{key}=$(_APR_BUILDDIR)\n", apr_rules_cnt, flags=re.MULTILINE)
                if nb == 0:
                    raise ConanException(f"Could not find/replace {key} in {apr_rules_mk}")
            open(apr_rules_mk, "w").write(apr_rules_cnt)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name",  "apr-1")
        prefix = "lib" if is_msvc(self) and self.options.shared else ""
        self.cpp_info.libs = [f"{prefix}apr-1"]
        self.cpp_info.resdirs = ["res"]
        if not self.options.shared:
            self.cpp_info.defines = ["APR_DECLARE_STATIC"]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs = ["crypt", "dl", "pthread", "rt"]
            if self.settings.os == "Windows":
                self.cpp_info.system_libs = ["mswsock", "rpcrt4", "ws2_32"]

        # TODO: to remove in conan v2
        self.env_info.APR_ROOT = self.package_folder
        self.env_info._APR_BUILDDIR = os.path.join(self.package_folder, "res", "build-1")
