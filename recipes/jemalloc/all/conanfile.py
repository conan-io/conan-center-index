from conans import AutoToolsBuildEnvironment, ConanFile, MSBuild, tools
from conans.errors import ConanInvalidConfiguration
from conans.client.tools import msvs_toolset
import os
import shutil
import string


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
        "prefix": "ANY",
        "enable_cxx": [True, False],
        "enable_fill": [True, False],
        "enable_xmalloc": [True, False],
        "enable_readlinkat": [True, False],
        "enable_syscall": [True, False],
        "enable_lazy_lock": [True, False],
        "enable_debug_logging": [True, False],
        "enable_initial_exec_tls": [True, False],
        "enable_libdl": [True, False],
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
    }

    _autotools = None

    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler.get_safe("libcxx") == "libc++":
            raise ConanInvalidConfiguration("libc++ is missing a mutex implementation.  Remove this when it is added")
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.version != "15":
            # https://github.com/jemalloc/jemalloc/issues/1703
            raise ConanInvalidConfiguration("Only Visual Studio 15 2017 is supported.  Please fix this if other versions are supported")
        if self.options.shared:
            del self.options.fPIC
        if not self.options.enable_cxx:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd
        if self.settings.build_type not in ("Release", "Debug", None):
            raise ConanInvalidConfiguration("Only Release and Debug build_types are supported")
        if self.settings.compiler == "Visual Studio" and self.settings.arch not in ("x86_64", "x86"):
            raise ConanInvalidConfiguration("Unsupported arch")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows and not os.environ.get("CONAN_BASH_PATH", None):
            self.build_requires("msys2/20190524")

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
            "--enable-initial-exec-tld" if self.options.enable_initial_exec_tls else "--disable-initial-exec-tls",
            "--enable-libdl" if self.options.enable_libdl else "--disable-libdl",
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        return conf_args

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.configure(args=self._autotools_args, configure_dir=self._source_subfolder)
        return self._autotools

    @property
    def _msvc_build_type(self):
        build_type = str(self.settings.build_type) or "Release"
        if not self.options.shared:
            build_type += "-static"
        return build_type

    def _patch_sources(self):
        if self.settings.os == "Windows":
            makefile_in = os.path.join(self._source_subfolder, "Makefile.in")
            tools.replace_in_file(makefile_in,
                                  "DSO_LDFLAGS = @DSO_LDFLAGS@",
                                  "DSO_LDFLAGS = @DSO_LDFLAGS@ -Wl,--out-implib,lib/libjemalloc.a")
            tools.replace_in_file(makefile_in,
                                  "\t$(INSTALL) -d $(LIBDIR)\n"
                                  "\t$(INSTALL) -m 755 $(objroot)lib/$(LIBJEMALLOC).$(SOREV) $(LIBDIR)",
                                  "\t$(INSTALL) -d $(BINDIR)\n"
                                  "\t$(INSTALL) -d $(LIBDIR)\n"
                                  "\t$(INSTALL) -m 755 $(objroot)lib/$(LIBJEMALLOC).$(SOREV) $(BINDIR)\n"
                                  "\t$(INSTALL) -m 644 $(objroot)lib/libjemalloc.a $(LIBDIR)")

    def build(self):
        self._patch_sources()
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
                with tools.environment_append({"CC": "cl", "CXX": "cl"}) if self.settings.compiler == "Visual Studio" else tools.no_op():
                    with tools.chdir(self._source_subfolder):
                        # Do not use AutoToolsBuildEnvironment because we want to run configure as ./configure
                        self.run("./configure {}".format(" ".join(self._autotools_args)), win_bash=tools.os_info.is_windows)
            msbuild = MSBuild(self)
            # Do not use the 2015 solution: unresolved external symbols: test_hooks_libc_hook and test_hooks_arena_new_hook
            sln_file = os.path.join(self._source_subfolder, "msvc", "jemalloc_vc2017.sln")
            msbuild.build(sln_file, targets=["jemalloc"], build_type=self._msvc_build_type)
        else:
            autotools = self._configure_autotools()
            autotools.make()

    @property
    def _library_name(self):
        libname = "jemalloc"
        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                if self.settings.build_type == "Debug":
                    libname += "d"
            else:
                toolset = msvs_toolset(self.settings)
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
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        if self.settings.compiler == "Visual Studio":
            arch_subdir = {
                "x86_64": "x64",
                "x86": "x86",
            }[str(self.settings.arch)]
            self.copy("*.lib", src=os.path.join(self._source_subfolder, "msvc", arch_subdir, self._msvc_build_type), dst=os.path.join(self.package_folder, "lib"))
            self.copy("*.dll", src=os.path.join(self._source_subfolder, "msvc", arch_subdir, self._msvc_build_type), dst=os.path.join(self.package_folder, "bin"))
            self.copy("jemalloc.h", src=os.path.join(self._source_subfolder, "include", "jemalloc"), dst=os.path.join(self.package_folder, "include", "jemalloc"), keep_path=True)
            shutil.copytree(os.path.join(self._source_subfolder, "include", "msvc_compat"),
                            os.path.join(self.package_folder, "include", "msvc_compat"))
        else:
            autotools = self._configure_autotools()
            # Use install_lib_XXX and install_include to avoid mixing binaries and dll's
            autotools.make(target="install_lib_shared" if self.options.shared else "install_lib_static")
            autotools.make(target="install_include")
            if self.settings.os == "Windows" and self.settings.compiler == "gcc":
                os.rename(os.path.join(self.package_folder, "lib", "{}.lib".format(self._library_name)),
                          os.path.join(self.package_folder, "lib", "lib{}.a".format(self._library_name)))
                if not self.options.shared:
                    os.unlink(os.path.join(self.package_folder, "lib", "jemalloc.lib"))

    def package_id(self):
        if not self.settings.build_type:
            self.info.settings.build_type = "Release"

    def package_info(self):
        self.cpp_info.libs = [self._library_name]
        self.cpp_info.includedirs = [os.path.join(self.package_folder, "include"),
                                     os.path.join(self.package_folder, "include", "jemalloc")]
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include", "msvc_compat"))
        if not self.options.shared:
            self.cpp_info.defines = ["JEMALLOC_EXPORT="]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread"])
