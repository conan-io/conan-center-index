from conan import ConanFile
from conan.tools.build import stdcpp_library
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rmdir, rm, rename, replace_in_file
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.scm import Version
from conan.tools.meson import Meson, MesonToolchain
from conan.errors import ConanInvalidConfiguration

import os


required_conan_version = ">=1.54.0"


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
    def _is_clang_cl(self):
        return self.settings.os == 'Windows' and self.settings.compiler == 'clang'

    @property
    def _preserve_dll_name(self):
        return (is_msvc(self) or self._is_clang_cl) and Version(self.version) <= "2.4.1" and self.options.shared

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        self.tool_requires("meson/1.4.1")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.2.0")
        if self.settings.arch in ["x86", "x86_64"]:
            self.tool_requires("nasm/2.16.01")

    def validate(self):
        if Version(self.version) <= "2.1.1" and self.settings.os in ["Android", "Macos"]:
            # INFO: ../src/meson.build:86:2: ERROR: Problem encountered: FIXME: Unhandled system android
            # INFO: ../src/meson.build:86:2: ERROR: Problem encountered: FIXME: Unhandled system darwin
            raise ConanInvalidConfiguration(f"{self.ref} does not support {self.settings.os}. Try a newer version.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = MesonToolchain(self)
        tc.project_options["tests"] = "disabled"
        tc.generate()

    def _patch_sources(self):
        if self._preserve_dll_name:
            # INFO: When generating with Meson, the library name is openh264-7.dll. This change preserves the old name openh264.dll
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "soversion: major_version,", "soversion: '',")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # INFO: Version 2.1.1 installs both static and shared libraries using same target name
        if Version(self.version) <= "2.1.1":
            if self.options.shared:
                rm(self, "*.a", os.path.join(self.package_folder, "lib"))
            else:
                rm(self, "*.so*", os.path.join(self.package_folder, "lib"))
                rm(self, "*.dylib*", os.path.join(self.package_folder, "lib"))
                rm(self, "*.dll", os.path.join(self.package_folder, "bin"))
                rm(self, "openh264.lib", os.path.join(self.package_folder, "lib"))

        if is_msvc(self) or self._is_clang_cl:
            rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))
            if self._preserve_dll_name:
                # INFO: Preserve same old library name as when building with Make on Windows but using Meson
                rename(self, os.path.join(self.package_folder, "lib", "openh264.lib"),
                    os.path.join(self.package_folder, "lib", "openh264_dll.lib"))
            else:
                rename(self, os.path.join(self.package_folder, "lib", "libopenh264.a"),
                    os.path.join(self.package_folder, "lib", "openh264.lib"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        suffix = "_dll" if self._preserve_dll_name else ""
        self.cpp_info.libs = [f"openh264{suffix}"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.extend(["m", "pthread"])
        if self.settings.os == "Android":
            self.cpp_info.system_libs.append("m")
        if not self.options.shared:
            libcxx = stdcpp_library(self)
            if libcxx:
                if self.settings.os == "Android" and libcxx == "c++_static":
                    # INFO: When builing for Android, need to link against c++abi too. Otherwise will get linkage errors:
                    # ld.lld: error: undefined symbol: operator new(unsigned long)
                    # >>> referenced by welsEncoderExt.cpp
                    self.cpp_info.system_libs.append("c++abi")
                self.cpp_info.system_libs.append(libcxx)
