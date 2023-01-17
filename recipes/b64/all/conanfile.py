from conan import ConanFile
from conan.tools.files import get, copy, chdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.microsoft import is_msvc, MSBuild, MSBuildToolchain
from conan.tools.layout import basic_layout
import os


required_conan_version = ">=1.53.0"


class B64Conan(ConanFile):
    name = "b64"
    description = "A library of ANSI C routines for fast encoding/decoding data into and from a base64-encoded format."
    license = "CC0-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://libb64.sourceforge.net/"
    topics = ("base64", "codec", "encoder", "decoder")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "static": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "static": False,
        "fPIC": True,
    }

    @property
    def _msvc_platform(self):
        return {
            "x86": "Win32",
            "x86_64": "Win32",
        }[str(self.settings.arch)]

    @property
    def _msbuild_configuration(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    @property
    def _msvc_directory(self):
        return os.path.join(self.source_folder, "base64", "VisualStudioProject");

    def _patch_sources_msvc(self):
        toolset = MSBuildToolchain(self).toolset
        replace_in_file(
            self,
            os.path.join(self._msvc_directory, "base64.vcxproj"),
            "<CharacterSet>Unicode</CharacterSet>",
            f"<CharacterSet>Unicode</CharacterSet>\n<PlatformToolset>{toolset}</PlatformToolset>",
        )
        replace_in_file(
            self,
            os.path.join(self._msvc_directory, "base64.vcxproj"),
            "H:\\builds\\libb64\\working.libb64\\include",
            os.path.join(self.source_folder, "include"),
        )

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.configuration = self._msbuild_configuration
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()

    def build(self):
        if is_msvc(self):
            self._patch_sources_msvc()

            msbuild = MSBuild(self)
            msbuild.platform = self._msvc_platform
            msbuild.build_type = self._msbuild_configuration
            msbuild.build(os.path.join(self._msvc_directory, "base64.sln"))
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.make(target="all_src")

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(
            self.package_folder, "licenses"), src=self.source_folder)
        copy(self, "*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"))
        copy(self, "*.a",
            dst=os.path.join(self.package_folder, "lib"),
            src=self.source_folder, keep_path=False)
        copy(self, "*.lib",
            dst=os.path.join(self.package_folder, "lib"),
            src=self.source_folder, keep_path=False)
        copy(self, "*.dll",
            dst=os.path.join(self.package_folder, "bin"),
            src=self.source_folder, keep_path=False)



    def package_info(self):
        self.cpp_info.libs = ["b64"]
