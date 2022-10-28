from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir, replace_in_file, rename
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.microsoft import is_msvc, MSBuildDeps, MSBuildToolchain, MSBuild, VCVars

from conan.tools.microsoft import msvc_runtime_flag
from conan.tools.microsoft.visual import msvc_version_to_vs_ide_version
from conans import tools as tools_legacy
import os
import re

required_conan_version = ">=1.52.0"


class LibVPXConan(ConanFile):
    name = "libvpx"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.webmproject.org/code"
    description = "WebM VP8/VP9 Codec SDK"
    topics = ("vpx", "codec", "web", "VP8", "VP9")
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
            try:
                del self.options.fPIC
            except Exception:
                pass

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Windows shared builds are not supported")
        if str(self.settings.compiler) not in ["Visual Studio", "msvc", "gcc", "clang", "apple-clang"]:
            raise ConanInvalidConfiguration("Unsupported compiler {}.".format(self.settings.compiler))
        if self.settings.os == "Macos" and self.settings.arch == "armv8" and tools.Version(self.version) < "1.10.0":
            raise ConanInvalidConfiguration("M1 only supported since 1.10, please upgrade")

    def layout(self):
        basic_layout(self, src_folder="src")

        # libvpx configure is unusual and requires a workaround,
        # look for "output_goes_here" below for more in this thread.
        self.cpp.package.bindirs = []
        self.cpp.package.includedirs = []
        self.cpp.package.libdirs = []

    def build_requirements(self):
        self.tool_requires("yasm/1.3.0")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def _patch_sources(self):
        apply_conandata_patches(self)
        # relocatable shared lib on macOS
# FIXME is this still needed?
        replace_in_file(self, os.path.join(self.source_folder, "build", "make", "Makefile"),
                              "-dynamiclib",
                              "-dynamiclib -install_name @rpath/$$(LIBVPX_SO)")
        # Disable LTO for Visual Studio when CFLAGS doesn't contain -GL
        if is_msvc(self):
# FIXME what is the proper way to do this?
            lto = any(re.finditer("(^| )[/-]GL($| )", tools.get_env("CFLAGS", "")))
            if not lto:
                replace_in_file(self,
                    os.path.join(self.source_folder, "build", "make", "gen_msvs_vcxproj.sh"),
                    "tag_content WholeProgramOptimization true",
                    "tag_content WholeProgramOptimization false",
                )

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
            compiler = "vs{}".format(vc_version)
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
        target = "%s-%s-%s" % (arch, os_name, compiler)
        tc.configure_args.append('--target=%s' % target)
        if str(self.settings.arch) in ["x86", "x86_64"]:
            for name in self._arch_options:
                if not self.options.get_safe(name):
                    tc.configure_args.append('--disable-%s' % name)

        if is_msvc(self):
            # gen_msvs_vcxproj.sh doesn't like custom flags
# FIXME what to do
            autotools.cxxflags = []
            autotools.flags = []
        if is_apple_os(self) and self.settings.get_safe("compiler.libcxx") == "libc++":
            # special case, as gcc/g++ is hard-coded in makefile, it implicitly assumes -lstdc++
# FIXME what to do
            autotools.link_flags.append("-stdlib=libc++")

        tc.generate()

        if is_msvc(self):
            tc = VCVars(self)
            tc.generate()


    def build(self):
        self._patch_sources()

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        # The workaround requires us to move the outputs into place now
        rename(self,
                os.path.join(self.package_folder, "output_goes_here", "include"),
                os.path.join(self.package_folder, "include")
                )
        rename(self,
                os.path.join(self.package_folder, "output_goes_here", "lib"),
                os.path.join(self.package_folder, "lib")
                )
        rmdir(self, os.path.join(self.package_folder, "output_goes_here"))

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        if is_msvc(self):
            # don't trust install target
            rmdir(self, os.path.join(self.package_folder, "lib"))
            libdir = os.path.join(
                "Win32" if self.settings.arch == "x86" else "x64",
                "Debug" if self.settings.build_type == "Debug" else "Release",
            )
            copy(self, "vpx*.lib", src=os.path.join(self.source_folder, libdir), dst=os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "vpx")
        suffix = msvc_runtime_flag(self).lower() if is_msvc(self) else ""
        self.cpp_info.libs = [f"vpx{suffix}"]
        if not self.options.shared:
            libcxx = tools_legacy.stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "vpx"
