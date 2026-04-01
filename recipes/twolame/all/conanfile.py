from conan import ConanFile
from conan.tools.microsoft import MSBuild, is_msvc
from conan.tools.files import copy, get, chdir, apply_conandata_patches, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.cmake import cmake_layout
import os

required_conan_version = ">=2.0"


class TwoLameConan(ConanFile):
    name = "twolame"
    description = "TwoLAME is an optimized MPEG Audio Layer 2 (MP2) encoder"
    license = "GNU"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/njh/twolame"
    topics = ("twolame", "audio")
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

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def generate(self):
        if not is_msvc(self):
            tc = AutotoolsToolchain(self)
            tc.generate()

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def build(self):
        if is_msvc(self):
            apply_conandata_patches(self)
            msbuild = MSBuild(self)
            sln = os.path.join(self.source_folder, "win32", "twolame_static.sln")
            if self.options.shared:
                sln = os.path.join(self.source_folder, "win32", "twolame.sln")
            msbuild.platform = "x64" if self.settings.arch == "x86_64" else "Win32"
            msbuild.build_type = self.settings.build_type
            msbuild.build(sln)
        else:
            with chdir(self, os.path.join(self.source_folder)):
                autotools = Autotools(self)
                autotools.configure()
                autotools.make()

    def package(self):
        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        dst_include_folder = os.path.join(self.package_folder, "include")
        include_folder = os.path.join(self.source_folder, "libtwolame")
        copy(self, pattern="*.h", src=include_folder, dst=dst_include_folder)

        dst_lib_folder = os.path.join(self.package_folder, "lib")
        if is_msvc(self):
            copy(self, pattern="*.lib", src=self.source_folder, dst=dst_lib_folder, keep_path=False)
            if self.options.shared:
                copy(self, pattern="*.dll", src=self.source_folder, dst=dst_lib_folder, keep_path=False)
        else:
            with chdir(self, os.path.join(self.source_folder)):
                autotools = Autotools(self)
                autotools.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "twolame")
        self.cpp_info.libs = ["twolame"]

        if self.settings.os == "Linux" or self.settings.os == "Macos":
            self.cpp_info.system_libs = ["m"]
