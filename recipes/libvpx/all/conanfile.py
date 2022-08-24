from conan.tools.microsoft import msvc_runtime_flag
from conan.tools.microsoft.visual import msvc_version_to_vs_ide_version
from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import functools
import os
import re

required_conan_version = ">=1.43.0"


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
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        if str(self.settings.arch) not in ['x86', 'x86_64']:
            for name in self._arch_options:
                delattr(self.options, name)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration("Windows shared builds are not supported")
        if str(self.settings.compiler) not in ["Visual Studio", "msvc", "gcc", "clang", "apple-clang"]:
            raise ConanInvalidConfiguration("Unsupported compiler {}.".format(self.settings.compiler))
        if self.settings.os == "Macos" and self.settings.arch == "armv8" and tools.Version(self.version) < "1.10.0":
            raise ConanInvalidConfiguration("M1 only supported since 1.10, please upgrade")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.build_requires("yasm/1.3.0")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # relocatable shared lib on macOS
        tools.replace_in_file(os.path.join(self._source_subfolder, "build", "make", "Makefile"),
                              "-dynamiclib",
                              "-dynamiclib -install_name @rpath/$$(LIBVPX_SO)")
        # Disable LTO for Visual Studio when CFLAGS doesn't contain -GL
        if self._is_msvc:
            lto = any(re.finditer("(^| )[/-]GL($| )", tools.get_env("CFLAGS", "")))
            if not lto:
                tools.replace_in_file(
                    os.path.join(self._source_subfolder, "build", "make", "gen_msvs_vcxproj.sh"),
                    "tag_content WholeProgramOptimization true",
                    "tag_content WholeProgramOptimization false",
                )

    @functools.lru_cache(1)
    def _configure_autotools(self):
        args = [
            "--prefix={}".format(tools.unix_path(self.package_folder)),
            "--disable-examples",
            "--disable-unit-tests",
            "--disable-tools",
            "--disable-docs",
            "--enable-vp9-highbitdepth",
            "--as=yasm",
        ]
        if self.options.shared:
            args.extend(['--disable-static', '--enable-shared'])
        else:
            args.extend(['--disable-shared', '--enable-static'])
        if self.settings.os != 'Windows' and self.options.get_safe("fPIC", True):
            args.append('--enable-pic')
        if self.settings.build_type == "Debug":
            args.append('--enable-debug')
        if self._is_msvc and "MT" in msvc_runtime_flag(self):
            args.append('--enable-static-msvcrt')

        arch = {'x86': 'x86',
                'x86_64': 'x86_64',
                'armv7': 'armv7',
                'armv8': 'arm64',
                'mips': 'mips32',
                'mips64': 'mips64',
                'sparc': 'sparc'}.get(str(self.settings.arch))
        if self._is_msvc:
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
        elif tools.is_apple_os(host_os):
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
        args.append('--target=%s' % target)
        if str(self.settings.arch) in ["x86", "x86_64"]:
            for name in self._arch_options:
                if not self.options.get_safe(name):
                    args.append('--disable-%s' % name)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if self._is_msvc:
            # gen_msvs_vcxproj.sh doesn't like custom flags
            autotools.cxxflags = []
            autotools.flags = []
        if tools.is_apple_os(self.settings.os) and self.settings.get_safe("compiler.libcxx") == "libc++":
            # special case, as gcc/g++ is hard-coded in makefile, it implicitly assumes -lstdc++
            autotools.link_flags.append("-stdlib=libc++")
        autotools.configure(args=args, configure_dir=self._source_subfolder, host=False, build=False, target=False)
        return autotools

    def build(self):
        self._patch_sources()
        with tools.vcvars(self) if self._is_msvc else tools.no_op():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        with tools.vcvars(self) if self._is_msvc else tools.no_op():
            autotools = self._configure_autotools()
            autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        if self._is_msvc:
            # don't trust install target
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib"))
            libdir = os.path.join(
                "Win32" if self.settings.arch == "x86" else "x64",
                "Debug" if self.settings.build_type == "Debug" else "Release",
            )
            self.copy("vpx*.lib", src=libdir, dst="lib")

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "vpx")
        suffix = msvc_runtime_flag(self).lower() if self._is_msvc else ""
        self.cpp_info.libs = [f"vpx{suffix}"]
        if not self.options.shared:
            libcxx = tools.stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "vpx"
