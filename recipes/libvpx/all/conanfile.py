from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file, rename
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, VCVars, unix_path, msvc_runtime_flag
from conan.tools.microsoft.visual import msvc_version_to_vs_ide_version
from conan.tools.scm import Version
from conans.tools import get_env # FIXME how to port this?
from conans.tools import stdcpp_library # TODO: import from conan.tools.build in conan 1.54.0 (https://github.com/conan-io/conan/pull/12269)
import os
import re

required_conan_version = ">=1.53.0"


class LibVPXConan(ConanFile):
    name = "libvpx"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.webmproject.org/code"
    description = "WebM VP8/VP9 Codec SDK"
    topics = "vpx", "codec", "web", "VP8", "VP9"
    license = "BSD-3-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _arch_options = ['mmx', 'sse', 'sse2', 'sse3', 'ssse3', 'sse4_1', 'avx', 'avx2', 'avx512']

    options.update({name: [True, False] for name in _arch_options})
    default_options.update({name: 'avx' not in name for name in _arch_options})

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        if str(self.settings.arch) not in ['x86', 'x86_64']:
            for name in self._arch_options:
                delattr(self.options, name)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Windows shared builds are not supported")
        if str(self.settings.compiler) not in ["Visual Studio", "msvc", "gcc", "clang", "apple-clang"]:
            raise ConanInvalidConfiguration(f"Unsupported compiler {self.settings.compiler}")
        if self.settings.os == "Macos" and self.settings.arch == "armv8" and Version(self.version) < "1.10.0":
            raise ConanInvalidConfiguration("M1 only supported since 1.10, please upgrade")

    def layout(self):
        basic_layout(self, src_folder="src")

        # libvpx configure is unusual and requires a workaround, otherwise it will fail with an error.
        # look for "output_goes_here" below for more in this thread.
        self.cpp.package.bindirs = []
        self.cpp.package.includedirs = []
        self.cpp.package.libdirs = []   # not strictly necessary, but lets do all as a group

    def build_requirements(self):
        self.tool_requires("yasm/1.3.0")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)

        # Note the output_goes_here workaround, libvpx does not like --prefix=/
        # as it fails the test for "libdir must be a subfolder of prefix"
        # libvpx src/build/make/configure.sh:683
        tc.configure_args.extend([
            "--prefix=/output_goes_here",
            "--libdir=/output_goes_here/lib",
            "--disable-examples",
            "--disable-unit-tests",
            "--disable-tools",
            "--disable-docs",
            "--enable-vp9-highbitdepth",
            "--as=yasm",
        ])
# FIXME is this handled by toolchain?
        if is_msvc(self) and "MT" in msvc_runtime_flag(self):
            tc.configure_args.append('--enable-static-msvcrt')

        arch = {'x86': 'x86',
                'x86_64': 'x86_64',
                'armv7': 'armv7',
                'armv8': 'arm64',
                'mips': 'mips32',
                'mips64': 'mips64',
                'sparc': 'sparc'}.get(str(self.settings.arch))
        if is_msvc(self):
            if self.settings.compiler == "Visual Studio":
                vc_version = self.settings.compiler.version
            else:
                vc_version = msvc_version_to_vs_ide_version(self.settings.compiler.version)
            compiler = f"vs{vc_version}"
        elif self.settings.compiler in ["gcc", "clang", "apple-clang"]:
            compiler = 'gcc'

        host_os = str(self.settings.os)
        if host_os == 'Windows':
            os_name = 'win32' if self.settings.arch == 'x86' else 'win64'
        elif is_apple_os(self):
            if self.settings.arch in ["x86", "x86_64"]:
                os_name = 'darwin11'
            elif self.settings.arch == "armv8" and self.settings.os == "Macos":
                os_name = 'darwin20'
            else:
                # Unrecognized toolchain 'arm64-darwin11-gcc', see list of toolchains in ./configure --help
                os_name = 'darwin'
        elif host_os == 'Linux':
            os_name = 'linux'
        elif host_os == 'Solaris':
            os_name = 'solaris'
        elif host_os == 'Android':
            os_name = 'android'
        target = f"{arch}-{os_name}-{compiler}"
        tc.configure_args.append(f"--target={target}")
        if str(self.settings.arch) in ["x86", "x86_64"]:
            for name in self._arch_options:
                if not self.options.get_safe(name):
                    tc.configure_args.append(f"--disable-{name}")

        if is_apple_os(self) and self.settings.get_safe("compiler.libcxx") == "libc++":
            # special case, as gcc/g++ is hard-coded in makefile, it implicitly assumes -lstdc++
# FIXME what to do
            tc.extra_ldflags.append("-stdlib=libc++")

        env = Environment()

        if is_msvc(self):
            # gen_msvs_vcxproj.sh doesn't like custom flags
            env.define("CC", "")
            # FIXME can we leave these alone?
            # env.define("CFLAGS", "")
            # env.define("CXXFLAGS", "")

        tc.generate(env=env)

        if is_msvc(self):
            tc = VCVars(self)
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        # Disable LTO for Visual Studio when CFLAGS doesn't contain -GL
        if is_msvc(self):
            self.output.info(f"CFLAGS = {get_env('CFLAGS', '')}")
            lto = any(re.finditer("(^| )[/-]GL($| )", get_env("CFLAGS", "")))
            if not lto:
                self.output.info("Disabling LTO")
                replace_in_file(self,
                    os.path.join(self.source_folder, "build", "make", "gen_msvs_vcxproj.sh"),
                    "tag_content WholeProgramOptimization true",
                    "tag_content WholeProgramOptimization false",
                )
            else:
                self.output.info("Enabling LTO")

        # The compile script wants to use CC for some of the platforms (Linux, etc),
        # but incorrectly assumes gcc is the compiler for those platforms.
        # This can fail some of the configure tests, and -lpthread isn't added to the link command.
        replace_in_file(self,
            os.path.join(self.source_folder, "build", "make", "configure.sh"),
            "  LD=${LD:-${CROSS}${link_with_cc:-ld}}",
            """
  LD=${LD:-${CROSS}${link_with_cc:-ld}}
  if [ "${link_with_cc}" = "gcc" ]
  then
   echo "using compiler as linker"
   LD=${CC}
  fi
"""
            )

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

        # Helpful lines for recipe debugging.  The configure script is not real autotools and is a pain to debug.
        # replace_in_file(self, os.path.join(self.source_folder, "configure"), "#!/bin/sh", "#!/bin/sh -x\nprintenv")
        # autotools = Autotools(self)
        # autotools.configure()
        # self.output.info("config.log file generated is:")
        # self.output.info(open(os.path.join(self.build_folder, "config.log")).read())
        # self.output.info("mk file generated is:")
        # self.output.info(open(os.path.join(self.build_folder, "libs-x86_64-linux-gcc.mk")).read())
        # autotools.make("SHELL='sh -x'")

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        # FIXME must use DESTDIR=unix_path, otherwise the install fails with messages about
        # "unable to install ..." and then every letter of the path split into a separate argument.
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])

        # The workaround requires us to move the outputs into place now
        rename(self,
                os.path.join(self.package_folder, "output_goes_here", "include"),
                os.path.join(self.package_folder, "include")
                )

        libs_from = os.path.join(self.package_folder, "output_goes_here", "lib")
        if is_msvc(self):
            # Libs may be in subfolders with lib folder
            libs_from = os.path.join(libs_from, "Win32" if self.settings.arch == "x86" else "x64")
        rename(self, libs_from, os.path.join(self.package_folder, "lib"))

        rmdir(self, os.path.join(self.package_folder, "output_goes_here"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        fix_apple_shared_install_name(self)


    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "vpx")
        suffix = msvc_runtime_flag(self).lower() if is_msvc(self) else ""
        self.cpp_info.libs = [f"vpx{suffix}"]
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("m")

        # reset the paths we cleared in layout()
        self.cpp_info.includedirs = ['include']
        self.cpp_info.libdirs = ['lib']
        self.cpp_info.bindirs = ['bin']

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "vpx"
