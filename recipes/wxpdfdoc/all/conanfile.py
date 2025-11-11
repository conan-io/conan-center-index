import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import collect_libs, copy, get, rmdir
from conan.tools.gnu import Autotools
from conan.tools.layout import basic_layout
from conan.tools.premake import Premake, PremakeDeps, PremakeToolchain

required_conan_version = ">=2.19.0"


class WxPdfDocConan(ConanFile):
    name = "wxpdfdoc"
    description = "wxPdfDocument allows wxWidgets applications to generate PDF documents."
    license = "WxWindows-exception-3.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://utelle.github.io/wxpdfdoc/"
    topics = ("wxwidgets", "pdf")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = '*'
    package_type = "library"
    options = { "shared": [True, False] }
    default_options = { "shared": False }
    generators = "AutotoolsDeps", "AutotoolsToolchain"

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        # Supports 3.0.x, 3.1.x and 3.2.x as defined in the repository readme
        self.requires("wxwidgets/[>=3.0.0 <3.3]", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        self.tool_requires("premake/5.0.0-beta7")

    def generate(self):
        if self.settings.os == "Windows":
            deps = PremakeDeps(self)
            deps.generate()
            tc = PremakeToolchain(self)
            tc.generate()

    def _arch_to_msbuild_platform(self, arch) -> str:
        platform_map = {
            "x86": "Win32",
            "x86_64": "Win64",
        }
        platform = platform_map.get(str(arch))
        if not platform:
            raise ConanInvalidConfiguration(f"Unsupported architecture: {arch}")
        return platform

    def _msvc_version_str(self) -> str:
        version_map = {
            "193": "vc17",
            "194": "vc17",
        }
        version = version_map.get(str(self.settings.compiler.version))
        if not version:
            raise ConanInvalidConfiguration(f"Unimplemented compiler version: {self.settings.compiler.version}")
        return version

    def build(self):
        if self.settings.os == "Windows":
            premake = Premake(self)
            premake.configure()
            platform = self._arch_to_msbuild_platform(self.settings.arch)
            premake.build(workspace=f"wxpdfdoc_{self._msvc_version_str()}", targets=["wxpdfdoc"], msbuild_platform=platform)
        else:
            wxwidgets_root = self.dependencies["wxwidgets"].package_folder
            autotools = Autotools(self)
            autotools.autoreconf()
            wx_config = os.path.join(wxwidgets_root, "bin", "wx-config")
            autotools.configure(args=[f"--with-wx-config={wx_config}"])
            autotools.make()

    def package(self):
        if self.settings.os == "Windows":
            copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
            lib_dir = os.path.join(self.source_folder, "lib")
            subdirs = [d for d in os.listdir(lib_dir) if os.path.isdir(os.path.join(lib_dir, d))]
            # Expecting one directory named something similar to "vc14x_x64_lib" and "fonts"
            assert len(subdirs) == 2, f"Expected exactly two subdirectories in {lib_dir}, found: {subdirs}"
            subdirs = sorted([d for d in subdirs if d.endswith("_lib")])
            copy(self, "*", os.path.join(self.source_folder, "lib", subdirs[0]), os.path.join(self.package_folder, "lib"))
            platform = self._arch_to_msbuild_platform(self.settings.arch)
            copy(self, "*", os.path.join(self.source_folder, "build-release", "lib", self._msvc_version_str(), platform, str(self.settings.build_type)), os.path.join(self.package_folder, "lib"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        copy(self, "LICENCE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["wxpdfdoc", "libwoff2", "libzint"]
        else:
            # Collect libraries with names like "wxcode_gtk2u_pdfdoc-3.2"
            self.cpp_info.libs = collect_libs(self, folder="lib")
