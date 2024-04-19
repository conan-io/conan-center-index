import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import chdir, copy, get, replace_in_file, rm
from conan.tools.gnu import AutotoolsToolchain, Autotools, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildToolchain, is_msvc, MSBuildDeps

required_conan_version = ">=1.47.0"


class GoogleGuetzliConan(ConanFile):
    name = "guetzli"
    description = "Perceptual JPEG encoder"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://opensource.google/projects/guetzli"
    topics = ("jpeg", "compression")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libpng/[>=1.6 <2]")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD", "Windows"]:
            raise ConanInvalidConfiguration(
                f"conan recipe for {self.ref} is not available in {self.settings.os}."
            )
        if str(self.settings.compiler.get_safe("libcxx")) == "libc++":
            raise ConanInvalidConfiguration(
                f"conan recipe for {self.ref} cannot be built with libc++"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.configuration = "Debug" if self.settings.build_type == "Debug" else "Release"
            tc.generate()
            deps = MSBuildDeps(self)
            deps.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    def _patch_sources(self):
        if is_msvc(self):
            # TODO: to remove once https://github.com/conan-io/conan/pull/12817 available in conan client
            platform_toolset = MSBuildToolchain(self).toolset
            import_conan_generators = ""
            for props_file in ["conantoolchain.props", "conandeps.props"]:
                props_path = os.path.join(self.generators_folder, props_file)
                if os.path.exists(props_path):
                    import_conan_generators += f"<Import Project=\"{props_path}\" />"
            vcxproj_file = os.path.join(self.source_folder, "guetzli.vcxproj")
            replace_in_file(self, vcxproj_file,
                            "<PlatformToolset>v140</PlatformToolset>",
                            f"<PlatformToolset>{platform_toolset}</PlatformToolset>")
            if props_path:
                replace_in_file(self, vcxproj_file,
                                '<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.targets" />',
                                f'{import_conan_generators}<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.targets" />')
        else:
            if self.settings.build_type not in ["Debug", "RelWithDebInfo"]:
                replace_in_file(self, os.path.join(self.source_folder, "guetzli.make"), " -g ", " ")

    def build(self):
        self._patch_sources()
        if is_msvc(self):
            msbuild = MSBuild(self)
            with chdir(self, self.source_folder):
                msbuild.build("guetzli.sln")
        else:
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.make()

    def package(self):
        for path in (self.source_path / "bin").rglob("guetzli*"):
            copy(self, path.name,
                 dst=os.path.join(self.package_folder, "bin"),
                 src=path.parent)
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []
