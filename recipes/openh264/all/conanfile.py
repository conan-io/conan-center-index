from conan import ConanFile
from conan.tools.build import stdcpp_library
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, replace_in_file, chdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path, msvc_runtime_flag

import os


required_conan_version = ">=1.57.0"


class OpenH264Conan(ConanFile):
    name = "openh264"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.openh264.org/"
    description = "Open Source H.264 Codec"
    topics = ("h264", "codec", "video", "compression", )
    license = "BSD-2-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_clang_cl(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'clang'

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self.settings.arch in ("x86", "x86_64"):
            self.tool_requires("nasm/2.15.05")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def _patch_sources(self):
        if is_msvc(self):
            replace_in_file(self, os.path.join(self.source_folder, "build", "platform-msvc.mk"),
                            "CFLAGS_OPT += -MT",
                            f"CFLAGS_OPT += -{msvc_runtime_flag(self)}")
            replace_in_file(self, os.path.join(self.source_folder, "build", "platform-msvc.mk"),
                            "CFLAGS_DEBUG += -MTd -Gm",
                            f"CFLAGS_DEBUG += -{msvc_runtime_flag(self)} -Gm")
        if self.settings.os == "Android":
            replace_in_file(self, os.path.join(self.source_folder, "codec", "build", "android", "dec", "jni", "Application.mk"),
                            "APP_STL := stlport_shared",
                            f"APP_STL := {self.settings.compiler.libcxx}")
            replace_in_file(self, os.path.join(self.source_folder, "codec", "build", "android", "dec", "jni", "Application.mk"),
                            "APP_PLATFORM := android-12",
                            f"APP_PLATFORM := {self._android_target}")

    @property
    def _library_filename(self):
        prefix = "" if (is_msvc(self) or self._is_clang_cl) else "lib"
        if self.options.shared:
            if is_apple_os(self):
                suffix = ".dylib"
            elif self.settings.os == "Windows":
                suffix = ".dll"
            else:
                suffix = ".so"
        else:
            if is_msvc(self) or self._is_clang_cl:
                suffix = ".lib"
            else:
                suffix = ".a"
        return prefix + "openh264" + suffix

    @property
    def _make_arch(self):
        return {
            "armv7": "arm",
            "armv8": "arm64",
            "x86": "i386",
        }.get(str(self.settings.arch), str(self.settings.arch))

    @property
    def _android_target(self):
        return f"android-{self.settings.os.api_level}"

    @property
    def _make_args(self):
        prefix = unix_path(self, os.path.abspath(self.package_folder))
        args = [
            f"ARCH={self._make_arch}",
            f"PREFIX={prefix}"
        ]

        if is_msvc(self) or self._is_clang_cl:
            args.append("OS=msvc")
        else:
            if self.settings.os == "Windows":
                args.append("OS=mingw_nt")
            if self.settings.os == "Android":
                libcxx = str(self.settings.compiler.libcxx)
                stl_lib = f'$(NDKROOT)/sources/cxx-stl/llvm-libc++/libs/$(APP_ABI)/lib{"c++_static.a" if libcxx == "c++_static" else "c++_shared.so"}' \
                          + "$(NDKROOT)/sources/cxx-stl/llvm-libc++/libs/$(APP_ABI)/libc++abi.a"
                ndk_home = os.environ["ANDROID_NDK_HOME"]
                args.extend([
                    f"NDKLEVEL={self.settings.os.api_level}",
                    f"STL_LIB={stl_lib}",
                    "OS=android",
                    f"NDKROOT={ndk_home}",  # not NDK_ROOT here
                    f"TARGET={self._android_target}",
                    "CCASFLAGS=$(CFLAGS) -fno-integrated-as",
                ])

        return args

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = AutotoolsToolchain(self)
        tc.make_args.extend(self._make_args)

        if is_msvc(self):
            tc.extra_cxxflags.append("-nologo")
            if check_min_vs(self, "180", raise_invalid=False):
                # https://github.com/conan-io/conan/issues/6514
                tc.extra_cxxflags.append("-FS")
        # not needed during and after 2.3.1
        elif self.settings.compiler in ("apple-clang",):
            if self.settings.arch in ("armv8",):
                tc.extra_ldflags.append("-arch arm64")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        self._patch_sources()
        autotools = Autotools(self)
        with chdir(self, self.source_folder):
            autotools.make(target=self._library_filename)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(
            self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        with chdir(self, self.source_folder):
            autotools.make(
                target=f'install-{"shared" if self.options.shared else "static-lib"}')

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "openh264")
        suffix = "_dll" if (
            is_msvc(self) or self._is_clang_cl) and self.options.shared else ""
        self.cpp_info.libs = [f"openh264{suffix}"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if self.settings.os == "Android":
            self.cpp_info.system_libs.append("m")
        libcxx = stdcpp_library(self)
        if libcxx:
            self.cpp_info.system_libs.append(libcxx)
