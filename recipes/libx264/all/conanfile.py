from conan import ConanFile
from conan.tools.apple import is_apple_os, XCRun, fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy, rename, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
import os

required_conan_version = ">=1.57.0"


class LibX264Conan(ConanFile):
    name = "libx264"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.videolan.org/developers/x264.html"
    description = "x264 is a free software library and application for encoding video streams into the " \
                  "H.264/MPEG-4 AVC compression format"
    topics = ("video", "encoding")
    license = "GPL-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "bit_depth": [8, 10, "all"],
        "with_opencl": [True, False],
        "with_asm": [True, False]
    }
    # The project by default enables opencl and asm, it can be opted-out
    default_options = {
        "shared": False,
        "fPIC": True,
        "bit_depth": "all",
        "with_opencl": True,
        "with_asm": True
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    @property
    def _with_nasm(self):
        return self.settings.arch in ("x86", "x86_64")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self._with_nasm:
            self.tool_requires("nasm/2.15.05")
        if self.settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)

        extra_asflags = []
        extra_cflags = []
        extra_ldflags = []
        args = {
            "--bit-depth": self.options.bit_depth,
            "--disable-cli": "",
            "--sbindir": None,          # Not understood by configure
            "--oldincludedir": None     # Not understood by configure
        }
        args["--disable-shared"] = None # --disable-shared is not understood
        if self.options.shared:
            args["--enable-shared"] = ""
        else:
            args["--enable-static"] = ""
        if not self.options.with_opencl:
            args["--disable-opencl"] = ""
        if not self.options.with_asm:
            args["--disable-asm"] = ""
        if self.options.get_safe("fPIC", self.settings.os != "Windows"):
            args["--enable-pic"] = ""
        if self.settings.build_type == "Debug":
            args["--enable-debug"] = ""

        if is_apple_os(self) and self.settings.arch == "armv8":
            # bitstream-a.S:29:18: error: unknown token in expression
            extra_asflags.append("-arch arm64")
            extra_ldflags.append("-arch arm64")
            args["--host"] = "aarch64-apple-darwin"
            if self.settings.os != "Macos": # TODO not sure why this is != "Macos" ... shouldn't it be == ??
                xcrun = XCRun(self)
                platform_flags = ["-isysroot", xcrun.sdk_path]
                apple_min_version_flag = AutotoolsToolchain(self).apple_min_version_flag
                if apple_min_version_flag:
                    platform_flags.append(apple_min_version_flag)
                extra_asflags.extend(platform_flags)
                extra_cflags.extend(platform_flags)
                extra_ldflags.extend(platform_flags)

        if self._with_nasm:
            env = Environment()
            env.define("AS", unix_path(self, os.path.join(self.dependencies.build["nasm"].package_folder, "bin", "nasm{}".format(".exe" if self.settings.os == "Windows" else ""))))
            env.vars(self).save_script("conanbuild_nasm")

        if cross_building(self):
            if self.settings.os == "Android":
                buildenv_vars = VirtualBuildEnv(self).vars()
                ndk_root = self.conf.get("tools.android:ndk_path", buildenv_vars.get("NDK_ROOT"))

                # INFO: Conan package android-ndk does not expose toolchain path. Looks fragile but follows always same for Android NDK
                build_os = {"Linux": "linux", "Macos": "darwin", "Windows": "windows"}.get(str(self.settings_build.os))
                toolchain = os.path.join(ndk_root, "toolchains", "llvm", "prebuilt", f"{build_os}-{self.settings_build.arch}")

                sysroot = self.conf.get("tools.build:sysroot", buildenv_vars.get("SYSROOT", f"{toolchain}/sysroot"))
                # INFO: x264 will look for strings appended to the cross prefix
                cross_prefix = os.path.join(toolchain, "bin", "llvm-")

                compilers_from_conf = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict)

                args["--build"] = None # --build is not recognized
                args["--cross-prefix"] = cross_prefix
                args["--sysroot"] = sysroot

                # the as of ndk does not work well for building libx264
                env = Environment()
                cc_as = compilers_from_conf.get("c", buildenv_vars.get("AS", "clang"))
                env.define("AS", cc_as)
                env_vars = env.vars(self, scope="build")
                env_vars.save_script("conanbuild_android")

        if is_msvc(self):
            env = Environment()
            env.define("CC", "cl -nologo")
            env.vars(self).save_script("conanbuild_msvc")

        if is_msvc(self) or self.settings.os in ["iOS", "watchOS", "tvOS"]:
            # autotools does not know about the msvc and Apple embedded OS canonical name(s)
            args["--build"] = None
            args["--host"] = None

        # The finite-math-only optimization has no effect and can cause linking errors
        # when linked against glibc >= 2.31
        extra_cflags += ["-fno-finite-math-only"]

        if extra_asflags:
            args["--extra-asflags"] = " ".join(extra_asflags)
        if extra_cflags:
            args["--extra-cflags"] = " ".join(extra_cflags)
        if extra_ldflags:
            args["--extra-ldflags"] = " ".join(extra_ldflags)
        tc.update_configure_args(args)
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if is_msvc(self):
            ext = ".dll.lib" if self.options.shared else ".lib"
            rename(self, os.path.join(self.package_folder, "lib", f"libx264{ext}"),
                         os.path.join(self.package_folder, "lib", "x264.lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "x264")
        self.cpp_info.libs = ["x264"]
        if is_msvc(self) and self.options.shared:
            self.cpp_info.defines.append("X264_API_IMPORTS")
        if self.settings.os in ["FreeBSD", "Linux"]:
            self.cpp_info.system_libs.extend(["dl", "pthread", "m"])
        elif self.settings.os == "Android":
            self.cpp_info.system_libs.extend(["dl", "m"])
