import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, rmdir, rm
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.premake import Premake, PremakeDeps, PremakeToolchain

# @todo 2.23.0 is not yet released but we require the configuration setting for Premake
# added in 86b5918763983683e4172fe21cb84d4fa98ec5fa
required_conan_version = ">=2.23.0"


class WxPdfDocConan(ConanFile):
    name = "wxpdfdoc"
    description = "wxPdfDocument allows wxWidgets applications to generate PDF documents."
    license = "WxWindows-exception-3.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://utelle.github.io/wxpdfdoc/"
    topics = ("wxwidgets", "pdf")
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = { "shared": [True, False], "fPIC": [True, False] }
    default_options = { "shared": False, "fPIC": True }
    implements = ["auto_shared_fpic"]
    exports_sources = '*'

    def _arch_to_msbuild_platform(self, arch):
        platform_map = {
            "x86": "Win32",
            "x86_64": "Win64",
        }
        platform = platform_map.get(str(arch))
        return platform

    def _msvc_version_str(self, compiler_version = None):
        if compiler_version is None:
            compiler_version = self.settings.compiler.version

        version_map = {
            "193": "vc17",
            "194": "vc17",
        }
        version = version_map.get(str(compiler_version))
        return version

    # https://github.com/utelle/wxsqlite3/issues/129#issuecomment-3527826225
    # The build files of wxSQLite3 contain 3 variations per Release resp Debug configuration:
    #   - Release / Debug : wxSQlite3 and wxWidgets as static libraries
    #   - Release DLL / Debug DLL : wxSQlite3 and wxWidgets as shared libraries
    #   - Release wxDLL / Debug wxDLL : wxSQlite3 as static library and wxWidgets as shared libraries
    def _get_configuration(self, wxwidgets_shared=None, wxpdfdoc_shared=None, build_type=None):
        if wxwidgets_shared is None:
            # @todo Why doesn't this properly work? I set '-o "wxwidgets/*:shared=True"' via the CLI
            # during 'conan create# but this returns None here...
            wxwidgets_shared = self.options["wxwidgets"].get_safe("shared")
            # @todo This line does not work at all....
            # wxwidgets_shared = self.options["wxwidgets"].shared
            #   ConanException: option 'shared' doesn't exist
        if wxpdfdoc_shared is None:
            wxpdfdoc_shared = self.options.shared
        if build_type is None:
            build_type = self.settings.build_type

        if wxpdfdoc_shared:
            suffix = "DLL"
        elif wxwidgets_shared:
            suffix = "wxDLL"
        else:
            suffix = ""

        config = f"{build_type} {suffix}".strip()
        # @todo Adjust for testing purposes but remove later
        config = "Release wxDLL"
        print(f"---------------------------------------------------------------------------------------------- Using configuration: {config}")
        return config

    def configure(self):
        if self.settings.os == "Windows" and self.options.shared:
            # There is no Premake configuration for building wxpdfdoc as shared library
            # and wxwidgets as static library.
            self.options["wxwidgets"].shared = True

    def validate(self):
        if self.settings.os == "Windows":
            platform = self._arch_to_msbuild_platform(self.settings.arch)
            if not platform:
                raise ConanInvalidConfiguration(f"Unsupported architecture: {self.settings.arch}")

            version = self._msvc_version_str()
            if not version:
                raise ConanInvalidConfiguration(f"Unimplemented compiler version: {self.settings.compiler.version}")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        # Supports 3.0.x, 3.1.x and 3.2.x as defined in the repository readme
        self.requires("wxwidgets/[>=3.2.5 <3.3]", transitive_headers=True, transitive_libs=True)

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.tool_requires("premake/5.0.0-beta7")
        else:
            self.tool_requires("libtool/2.4.7")

    def generate(self):
        if self.settings.os == "Windows":
            deps = PremakeDeps(self)
            deps.configuration = self._get_configuration()
            deps.generate()
            tc = PremakeToolchain(self)
            tc.generate()
        else:
            wxwidgets_root = self.dependencies["wxwidgets"].package_folder
            wx_config = os.path.join(wxwidgets_root, "bin", "wx-config")
            tc = AutotoolsToolchain(self)
            tc.configure_args.append(f"--with-wx-config={wx_config}")
            tc.generate()
            deps = AutotoolsDeps(self)
            deps.generate()

    def build(self):
        if self.settings.os == "Windows":
            premake = Premake(self)
            premake.configure()
            platform = self._arch_to_msbuild_platform(self.settings.arch)
            premake.build(workspace=f"wxpdfdoc_{self._msvc_version_str()}", targets=["wxpdfdoc"], msbuild_platform=platform, configuration=self._get_configuration())
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        if self.settings.os == "Windows":
            copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
            lib_dir = os.path.join(self.source_folder, "lib")
            subdirs = [d for d in os.listdir(lib_dir) if os.path.isdir(os.path.join(lib_dir, d))]
            subdir = sorted([d for d in subdirs if d != "fonts"])[0]
            copy(self, "*.lib", os.path.join(self.source_folder, "lib", subdir), os.path.join(self.package_folder, "lib"))

            if self.options.shared:
                copy(self, "*.dll", os.path.join(self.source_folder, "lib", subdir), os.path.join(self.package_folder, "bin"))

            platform = self._arch_to_msbuild_platform(self.settings.arch)
            copy(self, "*.lib", os.path.join(self.source_folder, "..", f"build-{str(self.settings.build_type).lower()}", "lib", self._msvc_version_str(), platform, self._get_configuration()), os.path.join(self.package_folder, "lib"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))

        copy(self, "LICENCE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.settings.build_type == "Release":
                self.cpp_info.libs = ["wxpdfdoc"]
            elif self.settings.build_type == "Debug":
                self.cpp_info.libs = ["wxpdfdocd"]
            self.cpp_info.libs += ["libwoff2", "libzint"]
        else:
            self.cpp_info.libs = ["wxcode_gtk2u_pdfdoc-3.2"]

# @todo Commands to test:
# conan create recipes/wxpdfdoc/all --build missing --version 1.3.1 --options shared=False -o "wxwidgets/*:shared=False" --settings build_type=Debug   #  Debug
# conan create recipes/wxpdfdoc/all --build missing --version 1.3.1 --options shared=False -o "wxwidgets/*:shared=False" --settings build_type=Release #  Release
# conan create recipes/wxpdfdoc/all --build missing --version 1.3.1 --options shared=False -o "wxwidgets/*:shared=True"  --settings build_type=Debug   #  Debug wxDLL
# conan create recipes/wxpdfdoc/all --build missing --version 1.3.1 --options shared=False -o "wxwidgets/*:shared=True"  --settings build_type=Release #  Release wxDLL
# conan create recipes/wxpdfdoc/all --build missing --version 1.3.1 --options shared=True  -o "wxwidgets/*:shared=False" --settings build_type=Debug   #  Invalid
# conan create recipes/wxpdfdoc/all --build missing --version 1.3.1 --options shared=True  -o "wxwidgets/*:shared=False" --settings build_type=Release #  Invalid
# conan create recipes/wxpdfdoc/all --build missing --version 1.3.1 --options shared=True  -o "wxwidgets/*:shared=True"  --settings build_type=Debug   #  Debug DLL
# conan create recipes/wxpdfdoc/all --build missing --version 1.3.1 --options shared=True  -o "wxwidgets/*:shared=True"  --settings build_type=Release #  Release DLL