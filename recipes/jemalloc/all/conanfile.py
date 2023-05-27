from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get, copy, rename
from conan.tools.microsoft import check_min_vs, is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import shutil

required_conan_version = ">=1.54.0"


class JemallocConan(ConanFile):
    name = "jemalloc"
    description = "jemalloc is a general purpose malloc(3) implementation that emphasizes fragmentation avoidance and scalable concurrency support."
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-2-Clause"
    homepage = "https://jemalloc.net/"
    topics = ("conan", "jemalloc", "malloc", "free")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "prefix": ["ANY"],
        "enable_cxx": [True, False],
        "enable_fill": [True, False],
        "enable_xmalloc": [True, False],
        "enable_readlinkat": [True, False],
        "enable_syscall": [True, False],
        "enable_lazy_lock": [True, False],
        "enable_debug_logging": [True, False],
        "enable_initial_exec_tls": [True, False],
        "enable_libdl": [True, False],
        "enable_prof": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "prefix": "",
        "enable_cxx": True,
        "enable_fill": True,
        "enable_xmalloc": False,
        "enable_readlinkat": False,
        "enable_syscall": True,
        "enable_lazy_lock": False,
        "enable_debug_logging": False,
        "enable_initial_exec_tls": True,
        "enable_libdl": True,
        "enable_prof": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _library_name(self):
        libname = "jemalloc"
        if self.settings.os == "Windows":
            if not self.options.shared:
                libname += "_s"
        else:
            if not self.options.shared and self.options.fPIC:
                libname += "_pic"
        return libname

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if not self.options.enable_cxx:
            self.settings.rm_safe("compiler.cppstd")
            self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.build_requires("automake/1.16.5")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def validate(self):
        # 1. MSVC specific checks
        if is_msvc(self):
            # The upstream repository provides solution files for Visual Studio 2015, 2017, 2019 and 2022,
            # but the 2015 solution does not work properly due to unresolved external symbols:
            # `test_hooks_libc_hook` and `test_hooks_arena_new_hook`
            check_min_vs(self, "191")
            # Building the shared library with a static MSVC runtime is not supported
            if self.options.shared and is_msvc_static_runtime(self):
                raise ConanInvalidConfiguration("Building the shared library with MT runtime is not supported.")
            # Only x86-64 and x86 are supported
            if self.settings.arch not in ["x86_64", "x86"]:
                raise ConanInvalidConfiguration(f"{self.settings.arch} is not supported.")
        # 2. Clang specific checks
        if self.settings.compiler == "clang":
            if Version(self.settings.compiler.version) <= "3.9":
                raise ConanInvalidConfiguration("Clang 3.9 or earlier is not supported.")
            if self.options.enable_cxx and self.settings.compiler.get_safe("libcxx") == "libc++" and \
                    Version(self.settings.compiler.version) < "10":
                raise ConanInvalidConfiguration("Clang 9 or earlier with libc++ is not supported due to the missing mutex implementation.")
        # 3. Verify the build type
        if self.settings.build_type not in ("Release", "Debug", None):
            raise ConanInvalidConfiguration("Only Release and Debug builds are supported.")
        # 4: Apple Silicon specific checks
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            if Version(self.version) < "5.3.0":
                raise ConanInvalidConfiguration("Support for Apple Silicon is only available as of 5.3.0.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            f"--with-jemalloc-prefix={self.options.prefix}",
            "--enable-debug" if self.settings.build_type == "Debug" else "--disable-debug",
            "--enable-cxx" if self.options.enable_cxx else "--disable-cxx",
            "--enable-fill" if self.options.enable_fill else "--disable-fill",
            "--enable-xmalloc" if self.options.enable_cxx else "--disable-xmalloc",
            "--enable-readlinkat" if self.options.enable_readlinkat else "--disable-readlinkat",
            "--enable-syscall" if self.options.enable_syscall else "--disable-syscall",
            "--enable-lazy-lock" if self.options.enable_lazy_lock else "--disable-lazy-lock",
            "--enable-log" if self.options.enable_debug_logging else "--disable-log",
            "--enable-initial-exec-tls" if self.options.enable_initial_exec_tls else "--disable-initial-exec-tls",
            "--enable-libdl" if self.options.enable_libdl else "--disable-libdl",
        ])
        if self.options.enable_prof:
            tc.configure_args.append("--enable-prof")
        if self.options.shared:
            tc.configure_args.append("--enable-shared")
            tc.configure_args.append("--disable-static")
        else:
            tc.configure_args.append("--disable-shared")
            tc.configure_args.append("--enable-static")
        env = tc.environment()
        if is_msvc(self):
            # Do not check whether the math library exists when compiled by MSVC
            # because MSVC treats the function `char log()` as a intrinsic function
            # and therefore complains about insufficient arguments passed to the function
            tc.configure_args.append("ac_cv_search_log=none required")
            env.define("CC", "cl")
            env.define("CXX", "cl")
        tc.generate(env)

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install(target="install_lib_shared" if self.options.shared else "install_lib_static")
        autotools.install(target="install_include")
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            rename(self, os.path.join(self.package_folder, "lib", f"{self._library_name}.lib"),
                         os.path.join(self.package_folder, "lib", f"lib{self._library_name}.a"))
            if not self.options.shared:
                os.unlink(os.path.join(self.package_folder, "lib", "jemalloc.lib"))
        if is_msvc(self):
            shutil.copytree(os.path.join(self.source_folder, "include", "msvc_compat"),
                            os.path.join(self.package_folder, "include", "msvc_compat"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "jemalloc")
        self.cpp_info.libs = [self._library_name]
        self.cpp_info.includedirs = [os.path.join(self.package_folder, "include"),
                                     os.path.join(self.package_folder, "include", "jemalloc")]
        if is_msvc(self):
            self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include", "msvc_compat"))
        if not self.options.shared:
            self.cpp_info.defines = ["JEMALLOC_EXPORT="]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread", "rt"])
