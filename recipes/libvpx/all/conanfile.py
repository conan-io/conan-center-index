import os
import re

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.build import stdcpp_library
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file, \
    rename
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, msvc_runtime_flag
from conan.tools.scm import Version

required_conan_version = ">=1.57.0"


class LibVPXConan(ConanFile):
    name = "libvpx"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.webmproject.org/code"
    description = "WebM VP8/VP9 Codec SDK"
    topics = "vpx", "codec", "web", "VP8", "VP9"
    license = "BSD-3-Clause"

    package_type = "library"
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
        if self.settings.os == "Windows":
            del self.options.shared
            self.package_type = "static-library"
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")
        if self.settings.os == "Android":
            del self.options.shared
            self.package_type = "static-library"

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if str(self.settings.compiler) not in ["Visual Studio", "msvc", "gcc", "clang", "apple-clang"]:
            raise ConanInvalidConfiguration(f"Unsupported compiler {self.settings.compiler}")
        if self.settings.os == "Macos" and self.settings.arch == "armv8" and Version(self.version) < "1.10.0":
            raise ConanInvalidConfiguration("M1 only supported since 1.10, please upgrade")
        if self.settings.os == "iOS" and (self.settings.os.sdk != "iphonesimulator" and self.settings.arch in ["x86_64", "x86"]):
            raise ConanInvalidConfiguration("iOS platform with x86/x86_64 architectures only supports 'iphonesimulator' SDK option")

    def build_requirements(self):
        self.tool_requires("yasm/1.3.0")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _install_tmp_folder(self):
        return "tmp_install"

    @property
    def _target_name(self):
        arch = {'x86': 'x86',
                'x86_64': 'x86_64',
                'armv7': 'armv7',
                'armv7s': 'armv7s',
                'armv8': 'arm64',
                'mips': 'mips32',
                'mips64': 'mips64',
                'sparc': 'sparc'}.get(str(self.settings.arch))
        compiler = str(self.settings.compiler)
        os_name = str(self.settings.os)
        if str(self.settings.compiler) == "Visual Studio":
            vc_version = self.settings.compiler.version
            compiler = f"vs{vc_version}"
        elif is_msvc(self):
            vc_version = str(self.settings.compiler.version)
            vc_version = {"170": "11", "180": "12", "190": "14", "191": "15", "192": "16", "193": "17", "194": "17"}[vc_version]
            compiler = f"vs{vc_version}"
        elif self.settings.compiler in ["gcc", "clang", "apple-clang"]:
            compiler = 'gcc'
        host_os = str(self.settings.os)
        if host_os == 'Windows':
            os_name = 'win32' if self.settings.arch == 'x86' else 'win64'
        elif is_apple_os(self):
            if self.settings.arch in ["x86", "x86_64"]:
                if self.settings.os == "Macos":
                    os_name = f'darwin11'
                else:
                    os_name = 'iphonesimulator'
            elif self.settings.arch == "armv8":
                os_name = 'darwin21'
            else:
                os_name = 'darwin'
        elif host_os == 'Linux':
            os_name = 'linux'
        elif host_os == 'Solaris':
            os_name = 'solaris'
        elif host_os == 'Android':
            os_name = 'android'
        return f"{arch}-{os_name}-{compiler}"

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)

        if is_apple_os(self) and self.settings.get_safe("compiler.libcxx") == "libc++":
            # special case, as gcc/g++ is hard-coded in makefile, it implicitly assumes -lstdc++
            tc.extra_ldflags.append("-stdlib=libc++")

        tc.configure_args.extend([
            "--disable-examples",
            "--disable-unit-tests",
            "--disable-tools",
            "--disable-docs",
            "--enable-vp9-highbitdepth",
            "--as=yasm",
        ])
        # Note for MSVC: release libs are always built, we just avoid keeping the release lib
        # Note2: Can't use --enable-debug_libs (to help install on Windows),
        #     the makefile's install step fails as it wants to install a library that doesn't exist.
        #     Instead, we will copy the desired library manually in the package step.
        if self.settings.build_type == "Debug":
            tc.configure_args.extend([
                "--enable-debug"
            ])
        if is_msvc(self) and is_msvc_static_runtime(self):
            tc.configure_args.append("--enable-static-msvcrt")
        if str(self.settings.arch) in ["x86", "x86_64"]:
            for name in self._arch_options:
                if not self.options.get_safe(name):
                    tc.configure_args.append(f"--disable-{name}")

        tc.update_configure_args({
            # libvpx does not like --prefix=/ as it fails the test for "libdir
            # must be a subfolder of prefix" libvpx src/build/make/configure.sh:683
            "--prefix": f"/{self._install_tmp_folder}",
            "--libdir": f"/{self._install_tmp_folder}/lib",
            # Needed to let libvpx use the correct toolchain for the target platform
            "--target": self._target_name,
            # several options must not be injected as custom configure doesn't like them
            "--host": None,
            "--build": None,
            "--bindir": None,
            "--sbindir": None,
            "--includedir": None,
            "--oldincludedir": None,
            "--datarootdir": None,
        })

        if is_msvc(self):
            # gen_msvs_vcxproj.sh doesn't like custom flags
            env = Environment()
            env.define("CC", "")
        else:
            env = tc.environment()
        tc.generate(env)

    def _patch_sources(self):
        apply_conandata_patches(self)
        # Disable LTO for Visual Studio when CFLAGS doesn't contain -GL
        if is_msvc(self):
            cflags = " ".join(self.conf.get("tools.build:cflags", default=[], check_type=list))
            lto = any(re.finditer("(^| )[/-]GL($| )", cflags))
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

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    @property
    def _lib_name(self):
        suffix = msvc_runtime_flag(self).lower() if is_msvc(self) else ""
        return f"vpx{suffix}"

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        # The workaround requires us to move the outputs into place now
        rename(self,
                os.path.join(self.package_folder, self._install_tmp_folder, "include"),
                os.path.join(self.package_folder, "include")
                )

        if is_msvc(self):
            # Libs are still in the build folder, get from there directly.
            # The makefile cannot correctly install the debug libs (see note about --enable-debug_libs)
            libs_from = os.path.join(
                    self.build_folder,
                    "Win32" if self.settings.arch == "x86" else "x64",
                    "Debug" if self.settings.build_type == "Debug" else "Release"
                    )
            # Copy for msvc, as it will generate a release and debug library, so take what we want
            # Note that libvpx's configure/make doesn't support shared lib builds on windows yet.
            copy(self, f"{self._lib_name}.lib", libs_from, os.path.join(self.package_folder, "lib"))
        else:
            # if not msvc, then libs were installed into package (in the wrong place), move them
            libs_from = os.path.join(self.package_folder, self._install_tmp_folder, "lib")
            rename(self, libs_from, os.path.join(self.package_folder, "lib"))

        rmdir(self, os.path.join(self.package_folder, self._install_tmp_folder))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "vpx")
        self.cpp_info.libs = [self._lib_name]
        if not self.options.get_safe("shared"):
            libcxx = stdcpp_library(self)
            if libcxx:
                self.cpp_info.system_libs.append(libcxx)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m", "pthread"])
