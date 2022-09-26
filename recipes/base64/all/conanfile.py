from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import Environment
from conan.tools.files import copy, get, apply_conandata_patches, chdir, export_conandata_patches, rmdir
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

import os

required_conan_version = ">=1.52.0"

class Base64Conan(ConanFile):
    name = "base64"
    description = "Fast Base64 stream encoder/decoder"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aklomp/base64"
    topics = ("base64", "codec", "encoder", "decoder")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        if self._use_cmake:
            cmake_layout(self, src_folder="src")
        else:
            basic_layout(self, src_folder="src")

    def validate(self):
        if Version(self.version) < "0.5.0" and self.info.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support build shared.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    @property
    def _use_cmake(self):
        return is_msvc(self) or Version(self.version) >= "0.5.0"

    def generate(self):
        if self._use_cmake:
            tc = CMakeToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()

    def build(self):
        apply_conandata_patches(self)
        if self._use_cmake:
            cmake = CMake(self)
            cmake.configure()
            if Version(self.version) >= "0.5.0":
                cmake.build()
            else:
                cmake.build(target="base64")
        else:
            env = Environment()
            if self.settings.arch == "x86" or self.settings.arch == "x86_64":
                env.append("AVX2_CFLAGS", "-mavx2")
                env.append("SSSE3_CFLAGS", "-mssse3")
                env.append("SSE41_CFLAGS", "-msse4.1")
                env.append("SSE42_CFLAGS", "-msse4.2")
                env.append("AVX_CFLAGS", "-mavx")
            else:
                # ARM-specific instructions can be enabled here
                pass
            with env.vars(self).apply(), \
                 chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.make(target="lib/libbase64.a")

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self._use_cmake:
            cmake = CMake(self)
            cmake.install()
            if Version(self.version) >= "0.5.0":
                rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
            else:
                rmdir(self, os.path.join(self.package_folder, "cmake"))
                rmdir(self, os.path.join(self.package_folder, "lib"))
                copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)
        else:
            copy(self, pattern="*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
            copy(self, pattern="*.a", dst=os.path.join(self.package_folder, "lib"), src=self.source_folder, keep_path=False)
            copy(self, pattern="*.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["base64"]

        if Version(self.version) >= "0.5.0" and self.options.shared:
            self.cpp_info.defines.append("BASE64_STATIC_DEFINE")
