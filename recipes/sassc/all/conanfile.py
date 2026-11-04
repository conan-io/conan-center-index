import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import chdir, copy, get, replace_in_file, save
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, is_msvc, MSBuildToolchain, MSBuildDeps

required_conan_version = ">=1.53.0"


class SasscConan(ConanFile):
    name = "sassc"
    description = "libsass command line driver"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sass-lang.com/libsass"
    topics = ("Sass", "compiler")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def config_options(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libsass/3.6.5")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if not is_msvc(self) and self.info.settings.os not in ["Linux", "FreeBSD", "Macos"]:
            raise ConanInvalidConfiguration(
                "sassc supports only Linux, FreeBSD, Macos and Windows Visual Studio at this time,"
                " contributions are welcomed"
            )

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _msbuild_configuration(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    @property
    def _msbuild_platform(self):
        return "Win32" if self.settings.arch == "x86" else "Win64"

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.configuration = self._msbuild_configuration
            tc.platform = self._msbuild_platform
            # FIXME: setting this property does not work, applied as a patch instead
            # tc.properties["LIBSASS_DIR"] = self.dependencies["libsass"].package_folder
            tc.generate()
            deps = MSBuildDeps(self)
            deps.configuration = self._msbuild_configuration
            deps.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()
            tc = AutotoolsToolchain(self)
            tc.configure_args += ["--disable-tests"]
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    def _patch_sources(self):
        platform_toolset = MSBuildToolchain(self).toolset
        import_conan_generators = ""
        for props_file in ["conantoolchain.props", "conandeps.props"]:
            props_path = os.path.join(self.generators_folder, props_file)
            if os.path.exists(props_path):
                import_conan_generators += f'<Import Project="{props_path}" />'
        vcxproj_file = os.path.join(self.source_folder, "win", "sassc.vcxproj")
        for existing_toolset in ["v120", "v140", "v141", "v142", "v143"]:
            replace_in_file(self, vcxproj_file,
                            f"<PlatformToolset>{existing_toolset}</PlatformToolset>",
                            f"<PlatformToolset>{platform_toolset}</PlatformToolset>", strict=False)
        # Inject VS 2022 support
        replace_in_file(self, vcxproj_file,
                        '<PropertyGroup Label="VS2019',
                        ('<PropertyGroup Label="VS2022 toolset selection" Condition="\'$(VisualStudioVersion)\' == \'17.0\'">\n'
                         f'  <PlatformToolset>{platform_toolset}</PlatformToolset>\n'
                         '</PropertyGroup>\n'
                         '<PropertyGroup Label="VS2019'))
        replace_in_file(self, vcxproj_file,
                        '<LIBSASS_DIR Condition="\'$(LIBSASS_DIR)\' == \'\'">..\\..</LIBSASS_DIR>',
                        f"<LIBSASS_DIR>{self.dependencies['libsass'].package_folder}</LIBSASS_DIR>")
        replace_in_file(self, vcxproj_file, r'<Import Project="$(LIBSASS_DIR)\win\libsass.targets" />', "")
        if props_path:
            replace_in_file(self, vcxproj_file,
                            r'<Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />',
                            rf'{import_conan_generators}<Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />')

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            if is_msvc(self):
                msbuild = MSBuild(self)
                msbuild.build_type = self._msbuild_configuration
                msbuild.platform = self._msbuild_platform
                msbuild.build(sln=os.path.join("win", "sassc.sln"))
            else:
                save(self, path="VERSION", content=f"{self.version}")
                autotools = Autotools(self)
                autotools.autoreconf()
                autotools.configure()
                autotools.make()

    def package(self):
        with chdir(self, self.source_folder):
            if is_msvc(self):
                copy(self, "*.exe",
                     dst=os.path.join(self.package_folder, "bin"),
                     src=os.path.join(self.source_folder, "bin"),
                     keep_path=False)
            else:
                autotools = Autotools(self)
                autotools.install()
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        # TODO: Legacy, to be removed on Conan 2.0
        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_folder)
