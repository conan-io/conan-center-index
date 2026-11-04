import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os, fix_apple_shared_install_name
from conan.tools.files import copy, download, get, rm, rmdir, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.microsoft import MSBuildToolchain, MSBuild
from conan.tools.layout import basic_layout

required_conan_version = ">=2.4"


class LibfabricConan(ConanFile):
    name = "libfabric"
    description = ("Libfabric, also known as Open Fabrics Interfaces (OFI), "
                   "defines a communication API for high-performance parallel and distributed applications.")
    license = ("BSD-2-Clause", "GPL-2.0-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://libfabric.org"
    topics = ("fabric", "communication", "framework", "service")

    package_type = "library"
    languages = "C"
    settings = "os", "arch", "compiler", "build_type"
    implements = ["auto_shared_fpic"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _msbuild_configuration(self):
        return "Debug-v142" if self.settings.build_type == "Debug" else "Release-v142"

    @property
    def _msbuild_platforms(self):
        return {"x86": "Win32", "x86_64": "x64"}.get(str(self.settings.arch), str(self.settings.arch))

    def configure(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
            self.options.rm_safe("shared")
            self.package_type = "shared-library"
        elif self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os == "Windows":
            if self.settings.arch != "x86_64":
                raise ConanInvalidConfiguration("Windows only supports x86_64 architecture. Build with -s arch=x84_64")
            # INFO: https://github.com/ofiwg/libfabric#windows-instructions
            self.output.warning("Libfabric on Windows requires Microsoft Network Direct SDK installed in your system. See https://github.com/ofiwg/libfabric#windows-instructions")

    def build_requirements(self):
        if self.settings.os != "Windows":
            # Used in ./configure tests and build
            self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        download(self, **self.conan_data["solution"][self.version], filename="libfabric.sln")

    def generate(self):
        if self.settings.os == "Windows":
            tc = MSBuildToolchain(self)
            tc.configuration = self._msbuild_configuration
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            if self.settings.build_type == "Debug":
                tc.configure_args.append("--enable-debug")
            tc.configure_args.append("--with-libnl=no")
            tc.configure_args.append("--enable-lpp=no")
            if is_apple_os(self):
                # INFO: The linker must reserve extra Mach-O header space or that step fails.
                tc.extra_ldflags.append("-headerpad_max_install_names")
            tc.generate()

    def _patch_sources(self):
        # INFO: Can not be used under source() because needs self.settings to determine the correct toolset.
        # INFO: Use toolset configured by Conan
        toolset = MSBuildToolchain(self).toolset
        vcxproj_path = os.path.join(self.source_folder, "libfabric.vcxproj")
        replace_in_file(self, vcxproj_path, "<PlatformToolset>v142</PlatformToolset>", f"<PlatformToolset>{toolset}</PlatformToolset>")
        # INFO: Inject Conan toolchain before Microsoft.Cpp.targets to ensure correct configuration of include and library paths, etc.
        conantoolchain_props = os.path.join(self.generators_folder, MSBuildToolchain.filename)
        replace_in_file(
            self, vcxproj_path,
            "<Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
            f"<Import Project=\"{conantoolchain_props}\" /><Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
        )

    def build(self):
        self._patch_sources()
        if self.settings.os == "Windows":
            msbuild = MSBuild(self)
            msbuild.build_type = self._msbuild_configuration
            sln_file = os.path.join(self.source_folder, "libfabric.sln")
            msbuild.build(sln_file, targets=["libfabric"])
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        if self.settings.os == "Windows":
            copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.source_folder, "include"))
            copy(self, "*.lib", dst=os.path.join(self.package_folder, "lib"), src=os.path.join(self.source_folder, self._msbuild_platforms, self._msbuild_configuration))
            copy(self, "*.dll", dst=os.path.join(self.package_folder, "bin"), src=os.path.join(self.source_folder, self._msbuild_platforms, self._msbuild_configuration))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "share"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "*.la", self.package_folder, recursive=True)
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["fabric"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m", "rt", "dl"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["Ws2_32", "user32", "gdi32", "winspool", "comdlg32", "advapi32"]
            self.cpp_info.includedirs.append(os.path.join("include", "windows"))
