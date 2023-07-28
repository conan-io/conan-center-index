import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, chdir, copy, get, export_conandata_patches
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildToolchain, is_msvc

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

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libpng/1.6.40")

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

    def _patch_sources(self):
        apply_conandata_patches(self)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()

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

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        # TODO: Legacy, to be removed on Conan 2.0
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
