from conan import ConanFile
from conan.tools.files import apply_conandata_patches, get, rename, replace_in_file, copy
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.microsoft import MSBuild, visual
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.layout import basic_layout
import os
import shutil
import string

required_conan_version = ">=1.58.0"

class JemallocConan(ConanFile):
    name = "jemalloc"
    description = "jemalloc is a general purpose malloc(3) implementation that emphasizes fragmentation avoidance and scalable concurrency support."
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-2-Clause"
    homepage = "http://jemalloc.net/"
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
    exports_sources = ["patches/**"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            
    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--enable-debug" if self.settings.build_type == "Debug" else "--disable-debug")
        tc.configure_args.append("--enable-cxx" if self.options.enable_cxx else "--disable-cxx")
        tc.configure_args.append("--enable-fill" if self.options.enable_fill else "--disable-fill")
        tc.configure_args.append("--enable-xmalloc" if self.options.enable_cxx else "--disable-xmalloc")
        tc.configure_args.append("--enable-readlinkat" if self.options.enable_readlinkat else "--disable-readlinkat")
        tc.configure_args.append("--enable-syscall" if self.options.enable_syscall else "--disable-syscall")
        tc.configure_args.append("--enable-lazy-lock" if self.options.enable_lazy_lock else "--disable-lazy-lock")
        tc.configure_args.append("--enable-log" if self.options.enable_debug_logging else "--disable-log")
        tc.configure_args.append("--enable-initial-exec-tls" if self.options.enable_initial_exec_tls else "--disable-initial-exec-tls")
        tc.configure_args.append("--enable-libdl" if self.options.enable_libdl else "--disable-libdl")
        if self.options.prefix:
            tc.configure_args["--with-jemalloc-prefix"] = self.options.prefix
        if self.options.enable_prof:
            tc.configure_args.append("--enable-prof")
        tc.generate()

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.enable_cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def validate(self):
        if self.options.enable_cxx and \
                self.settings.compiler.get_safe("libcxx") == "libc++" and \
                self.settings.compiler == "clang" and \
                Version(self.settings.compiler.version) < "10":
            raise ConanInvalidConfiguration("clang and libc++ version {} (< 10) is missing a mutex implementation".format(self.settings.compiler.version))
        if visual.is_msvc(self) and self.options.shared and \
                "MT" in self.settings.compiler.runtime:
            raise ConanInvalidConfiguration("Visual Studio build for shared library with MT runtime is not supported")
        if visual.is_msvc(self) and self.settings.compiler.version != "15":
            # https://github.com/jemalloc/jemalloc/issues/1703
            raise ConanInvalidConfiguration("Only Visual Studio 15 2017 is supported.  Please fix this if other versions are supported")
        if self.settings.build_type not in ("Release", "Debug", None):
            raise ConanInvalidConfiguration("Only Release and Debug build_types are supported")
        if visual.is_msvc(self) and self.settings.arch not in ("x86_64", "x86"):
            raise ConanInvalidConfiguration("Unsupported arch")
        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) <= "3.9":
            raise ConanInvalidConfiguration("Unsupported compiler version")
        if self.settings.os == "Macos" and self.settings.arch not in ("x86_64", "x86"):
            raise ConanInvalidConfiguration("Unsupported arch")

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not self.conf.get("tools.microsoft.bash:path", default=False, check_type=bool):
            self.build_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    @property
    def _msvc_build_type(self):
        build_type = str(self.settings.build_type) or "Release"
        if not self.options.shared:
            build_type += "-static"
        return build_type

    def _patch_sources(self):
        if self.settings.os == "Windows":
            makefile_in = os.path.join(self.source_folder, "Makefile.in")
            replace_in_file(self, makefile_in,
                                  "DSO_LDFLAGS = @DSO_LDFLAGS@",
                                  "DSO_LDFLAGS = @DSO_LDFLAGS@ -Wl,--out-implib,lib/libjemalloc.a", strict=False)
            replace_in_file(self, makefile_in,
                                  "\t$(INSTALL) -d $(LIBDIR)\n"
                                  "\t$(INSTALL) -m 755 $(objroot)lib/$(LIBJEMALLOC).$(SOREV) $(LIBDIR)",
                                  "\t$(INSTALL) -d $(BINDIR)\n"
                                  "\t$(INSTALL) -d $(LIBDIR)\n"
                                  "\t$(INSTALL) -m 755 $(objroot)lib/$(LIBJEMALLOC).$(SOREV) $(BINDIR)\n"
                                  "\t$(INSTALL) -m 644 $(objroot)lib/libjemalloc.a $(LIBDIR)", strict=False)

        apply_conandata_patches(self)

    # TODO: Remove once Windows has been migrated to conan 2.x
    @property
    def _autotools_args(self):
        conf_args = [
            "--with-jemalloc-prefix={}".format(self.options.prefix),
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
        ]
        if self.options.enable_prof:
            conf_args.append("--enable-prof")
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        return conf_args

    def build(self):
        self._patch_sources()
        if visual.is_msvc(self):
            # TODO: someone on windows can fix this up, should still work of conan 1.x
            from conans import tools as tools_legacy
            with tools_legacy.vcvars(self.settings):
                with tools_legacy.environment_append({"CC": "cl", "CXX": "cl"}):
                    with tools_legacy.chdir(self.source_folder):
                        # Do not use AutoToolsBuildEnvironment because we want to run configure as ./configure
                        self.run("./configure {}".format(" ".join(self._autotools_args)), win_bash=tools_legacy.os_info.is_windows)
            msbuild = MSBuild(self)
            # Do not use the 2015 solution: unresolved external symbols: test_hooks_libc_hook and test_hooks_arena_new_hook
            sln_file = os.path.join(self.source_folder, "msvc", "jemalloc_vc2017.sln")
            msbuild.build(sln_file, targets=["jemalloc"])
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    @property
    def _library_name(self):
        libname = "jemalloc"
        if visual.is_msvc(self):
            if self.options.shared:
                if self.settings.build_type == "Debug":
                    libname += "d"
            else:
                # TODO: someone on windows can fix this up, should still work of conan 1.x
                from conans import tools as tools_legacy
                toolset = tools_legacy.msvs_toolset(self.settings)
                toolset_number = "".join(c for c in toolset if c in string.digits)
                libname += "-vc{}-{}".format(toolset_number, self._msvc_build_type)
        else:
            if self.settings.os == "Windows":
                if not self.options.shared:
                    libname += "_s"
            else:
                if not self.options.shared and self.options.fPIC:
                    libname += "_pic"
        return libname

    def package(self):
        copy(self, pattern="COPYING", src=self.source_folder, dst="licenses")
        if visual.is_msvc(self):
            arch_subdir = {
                "x86_64": "x64",
                "x86": "x86",
            }[str(self.settings.arch)]
            copy(self, "*.lib", src=os.path.join(self.source_folder, "msvc", arch_subdir, self._msvc_build_type), dst=os.path.join(self.package_folder, "lib"))
            copy(self, "*.dll", src=os.path.join(self.source_folder, "msvc", arch_subdir, self._msvc_build_type), dst=os.path.join(self.package_folder, "bin"))
            copy(self, "jemalloc.h", src=os.path.join(self.source_folder, "include", "jemalloc"), dst=os.path.join(self.package_folder, "include", "jemalloc"), keep_path=True)
            shutil.copytree(os.path.join(self.source_folder, "include", "msvc_compat"),
                            os.path.join(self.package_folder, "include", "msvc_compat"))
        else:
            autotools = Autotools(self)
            autotools.configure()
            # Use install_lib_XXX and install_include to avoid mixing binaries and dll's
            autotools.install(target="install_lib_shared" if self.options.shared else "install_lib_static")
            autotools.install(target="install_include")
            if self.settings.os == "Windows" and self.settings.compiler == "gcc":
                rename(self, os.path.join(self.package_folder, "lib", "{}.lib".format(self._library_name)),
                             os.path.join(self.package_folder, "lib", "lib{}.a".format(self._library_name)))
                if not self.options.shared:
                    os.unlink(os.path.join(self.package_folder, "lib", "jemalloc.lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "jemalloc")
        self.cpp_info.libs = [self._library_name]
        self.cpp_info.includedirs = [os.path.join(self.package_folder, "include"),
                                     os.path.join(self.package_folder, "include", "jemalloc")]
        if visual.is_msvc(self):
            self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include", "msvc_compat"))
        if not self.options.shared:
            self.cpp_info.defines = ["JEMALLOC_EXPORT="]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread", "rt"])
