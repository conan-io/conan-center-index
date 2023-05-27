from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, get, copy, rename, replace_in_file
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime
from conan.tools.scm import Version
import os

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
        if str(self.settings.compiler) in ["Visual Studio", "msvc"]:
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
                raise ConanInvalidConfiguration(f"Clang 9 or earlier with libc++ is not supported due to the missing mutex implementation.")
        # 3. Verify the build type
        if self.settings.build_type not in ("Release", "Debug", None):
            raise ConanInvalidConfiguration("Only Release and Debug builds are supported.")

        # jemalloc seems to support Apple Silicon Macs (Reference: Homebrew)
        # if self.settings.os == "Macos" and self.settings.arch not in ("x86_64", "x86"):
        #     raise ConanInvalidConfiguration("Unsupported arch")

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
        if str(self.settings.compiler) in ["Visual Studio", "msvc"]:
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
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="COPYING*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install(target="install_lib_shared" if self.options.shared else "install_lib_static")
        autotools.install(target="install_include")


        # if self.settings.compiler == "Visual Studio":
        #     arch_subdir = {
        #         "x86_64": "x64",
        #         "x86": "x86",
        #     }[str(self.settings.arch)]
        #     self.copy("*.lib", src=os.path.join(self.source_folder, "msvc", arch_subdir, self._msvc_build_type), dst=os.path.join(self.package_folder, "lib"))
        #     self.copy("*.dll", src=os.path.join(self.source_folder, "msvc", arch_subdir, self._msvc_build_type), dst=os.path.join(self.package_folder, "bin"))
        #     self.copy("jemalloc.h", src=os.path.join(self.source_folder, "include", "jemalloc"), dst=os.path.join(self.package_folder, "include", "jemalloc"), keep_path=True)
        #     shutil.copytree(os.path.join(self.source_folder, "include", "msvc_compat"),
        #                     os.path.join(self.package_folder, "include", "msvc_compat"))
        # else:
        #     autotools = self._configure_autotools()
        #     # Use install_lib_XXX and install_include to avoid mixing binaries and dll's
        #     autotools.make(target="install_lib_shared" if self.options.shared else "install_lib_static")
        #     autotools.make(target="install_include")
        #     if self.settings.os == "Windows" and self.settings.compiler == "gcc":
        #         rename(self, os.path.join(self.package_folder, "lib", "{}.lib".format(self._library_name)),
        #                      os.path.join(self.package_folder, "lib", "lib{}.a".format(self._library_name)))
        #         if not self.options.shared:
        #             os.unlink(os.path.join(self.package_folder, "lib", "jemalloc.lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "jemalloc")
        self.cpp_info.libs = [self._library_name]
        self.cpp_info.includedirs = [os.path.join(self.package_folder, "include"),
                                     os.path.join(self.package_folder, "include", "jemalloc")]
        if self.settings.compiler == "msvc":
            self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include", "msvc_compat"))
        if not self.options.shared:
            self.cpp_info.defines = ["JEMALLOC_EXPORT="]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread", "rt"])

    # @property
    # def _msvc_build_type(self):
    #     build_type = str(self.settings.build_type) or "Release"
    #     if not self.options.shared:
    #         build_type += "-static"
    #     return build_type

    # def _patch_sources(self): # TODO: Is this necessary???
    #     if self.settings.os == "Windows":
    #         makefile_in = os.path.join(self.source_folder, "Makefile.in")
    #         replace_in_file(self, makefile_in,
    #                               "DSO_LDFLAGS = @DSO_LDFLAGS@",
    #                               "DSO_LDFLAGS = @DSO_LDFLAGS@ -Wl,--out-implib,lib/libjemalloc.a", strict=False)
    #         replace_in_file(self, makefile_in,
    #                               "\t$(INSTALL) -d $(LIBDIR)\n"
    #                               "\t$(INSTALL) -m 755 $(objroot)lib/$(LIBJEMALLOC).$(SOREV) $(LIBDIR)",
    #                               "\t$(INSTALL) -d $(BINDIR)\n"
    #                               "\t$(INSTALL) -d $(LIBDIR)\n"
    #                               "\t$(INSTALL) -m 755 $(objroot)lib/$(LIBJEMALLOC).$(SOREV) $(BINDIR)\n"
    #                               "\t$(INSTALL) -m 644 $(objroot)lib/libjemalloc.a $(LIBDIR)", strict=False)
    #
    #     apply_conandata_patches(self)


    # def build(self):
    #     self._patch_sources()
    #     if self.settings.compiler == "Visual Studio":
    #         with tools_legacy.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools_legacy.no_op():
    #             with tools_legacy.environment_append({"CC": "cl", "CXX": "cl"}) if self.settings.compiler == "Visual Studio" else tools_legacy.no_op():
    #                 with tools_legacy.chdir(self.source_folder):
    #                     # Do not use AutoToolsBuildEnvironment because we want to run configure as ./configure
    #                     self.run("./configure {}".format(" ".join(self._autotools_args)), win_bash=tools_legacy.os_info.is_windows)
    #         msbuild = MSBuild(self)
    #         # Do not use the 2015 solution: unresolved external symbols: test_hooks_libc_hook and test_hooks_arena_new_hook
    #         sln_file = os.path.join(self.source_folder, "msvc", "jemalloc_vc2017.sln")
    #         msbuild.build(sln_file, targets=["jemalloc"], build_type=self._msvc_build_type)
    #     else:
    #         autotools = self._configure_autotools()
    #         autotools.make()

    # @property
    # def _library_name(self):
    #     libname = "jemalloc"
    #     if self.settings.compiler == "Visual Studio":
    #         if self.options.shared:
    #             if self.settings.build_type == "Debug":
    #                 libname += "d"
    #         else:
    #             toolset = tools_legacy.msvs_toolset(self.settings)
    #             toolset_number = "".join(c for c in toolset if c in string.digits)
    #             libname += "-vc{}-{}".format(toolset_number, self._msvc_build_type)
    #     else:
    #         if self.settings.os == "Windows":
    #             if not self.options.shared:
    #                 libname += "_s"
    #         else:
    #             if not self.options.shared and self.options.fPIC:
    #                 libname += "_pic"
    #     return libname

    # def package(self):
    #     self.copy(pattern="COPYING", src=self.source_folder, dst="licenses")
    #     if self.settings.compiler == "Visual Studio":
    #         arch_subdir = {
    #             "x86_64": "x64",
    #             "x86": "x86",
    #         }[str(self.settings.arch)]
    #         self.copy("*.lib", src=os.path.join(self.source_folder, "msvc", arch_subdir, self._msvc_build_type), dst=os.path.join(self.package_folder, "lib"))
    #         self.copy("*.dll", src=os.path.join(self.source_folder, "msvc", arch_subdir, self._msvc_build_type), dst=os.path.join(self.package_folder, "bin"))
    #         self.copy("jemalloc.h", src=os.path.join(self.source_folder, "include", "jemalloc"), dst=os.path.join(self.package_folder, "include", "jemalloc"), keep_path=True)
    #         shutil.copytree(os.path.join(self.source_folder, "include", "msvc_compat"),
    #                         os.path.join(self.package_folder, "include", "msvc_compat"))
    #     else:
    #         autotools = self._configure_autotools()
    #         # Use install_lib_XXX and install_include to avoid mixing binaries and dll's
    #         autotools.make(target="install_lib_shared" if self.options.shared else "install_lib_static")
    #         autotools.make(target="install_include")
    #         if self.settings.os == "Windows" and self.settings.compiler == "gcc":
    #             rename(self, os.path.join(self.package_folder, "lib", "{}.lib".format(self._library_name)),
    #                          os.path.join(self.package_folder, "lib", "lib{}.a".format(self._library_name)))
    #             if not self.options.shared:
    #                 os.unlink(os.path.join(self.package_folder, "lib", "jemalloc.lib"))
    #
    # def package_info(self):
    #     self.cpp_info.names["pkg_config"] = "jemalloc"
    #     self.cpp_info.libs = [self._library_name]
    #     self.cpp_info.includedirs = [os.path.join(self.package_folder, "include"),
    #                                  os.path.join(self.package_folder, "include", "jemalloc")]
    #     if self.settings.compiler == "Visual Studio":
    #         self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include", "msvc_compat"))
    #     if not self.options.shared:
    #         self.cpp_info.defines = ["JEMALLOC_EXPORT="]
    #     if self.settings.os in ["Linux", "FreeBSD"]:
    #         self.cpp_info.system_libs.extend(["dl", "pthread", "rt"])
