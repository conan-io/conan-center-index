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
            msg = ("apr recipe doesn't support cross-build for all the platforms"
                   " due to runtime checks in autoconf. You can provide"
                   " a pre-built cached file as an user Conan conf variable to try it.\n\n"
                   "Via host profile:\n"
                   "[conf]\nuser.apr:cache_file=/path/to/cache_file\n\n"
                   "Via CLI: \n"
                   "-c \"user.apr:cache_file='/path/to/cache_file'\"")
            # Cross-building for apr < 1.7.4 is not supported without a pre-built cached file
            if Version(self.version) < "1.7.4" and self.conf.get("user.apr:cache_file") is None:
                raise ConanInvalidConfiguration(msg)
            # Conan provides for apr >= 1.7.4 and Linux some configuration flags to avoid
            # entering a pre-built cached file
            if self.settings.os != "Linux" and self.conf.get("user.apr:cache_file") is None:
                raise ConanInvalidConfiguration(msg)

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
        The vast majority of projects that use autotools and make use of the AC_TRY_RUN macro,
        do provide a default fallback when cross-compiling, as per the documentation here:

            * https://ftp.gnu.org/old-gnu/Manuals/autoconf-2.53/html_node/Test-Programs.html

        In that regard, APR cannot be cross-compiled by traditional means, and the only fallback
        is to use a cache file. Indeed, the only way to cross-compile that is documented by upstream
        is by pre-empting the configuration checks with a cache file that needs to be generated on
        the target system:

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
        if self.settings.os == "Linux":
            # Mandatory cross-building configuration flags (tested on Linux ARM and Intel)
            configure_args.extend(["apr_cv_mutex_robust_shared=yes",
                                   "ac_cv_file__dev_zero=yes",
                                   "apr_cv_process_shared_works=yes",
                                   "apr_cv_tcp_nodelay_with_cork=yes"])
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
