import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildToolchain, is_msvc, check_min_vs

required_conan_version = ">=2.0"

class PackageConan(ConanFile):
    name = "opencppcoverage"
    description = "OpenCppCoverage is an open source code coverage tool for C++ under Windows."
    license = "GPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/OpenCppCoverage/OpenCppCoverage"
    topics = ("coverage", "test", "debug")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if not is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} can be built only by Visual Studio and msvc.")

        if not check_min_vs(self, "192"):
            raise ConanInvalidConfiguration("Visual Studio 2019 (version 192) or higher is required.")

        if not self.settings.arch in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration(f"{self.ref} can be built only for x86 or x64.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _msbuild_configuration(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    @property
    def _msbuild_platform(self):
        return "x64" if self.settings.arch == "x86_64" else "Win32"

    def generate(self):
        tc = MSBuildToolchain(self)
        tc.configuration = self._msbuild_configuration
        tc.generate()

    def build(self):
        self.run("powershell -ExecutionPolicy Bypass -File InstallThirdPartyLibraries.ps1",
                 cwd=self.source_folder)

        msbuild = MSBuild(self)
        msbuild.build_type = self._msbuild_configuration
        msbuild.platform = self._msbuild_platform
        msbuild_command = msbuild.command(sln="CppCoverage.sln")

        self.run(msbuild_command, cwd=self.source_folder)

    def package(self):
        build_output = os.path.join(
            self.source_folder,
            "x64" if self.settings.arch == "x86_64" else "",
            self._msbuild_configuration)

        install_bin = os.path.join(
            self.package_folder,
            "bin")

        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*.dll", build_output, install_bin)
        copy(self, "*.exe", build_output, install_bin)
        copy(self, "Template/*", build_output, install_bin)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bindir)
