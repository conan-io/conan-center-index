from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir, export_conandata_patches, apply_conandata_patches, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.microsoft import is_msvc, MSBuild, MSBuildDeps, MSBuildToolchain
import os

required_conan_version = ">=2.1"

class ReadstatConan(ConanFile):
    name = "readstat"
    description = "Command-line tool (+ C library) for converting SAS, Stata, and SPSS files"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/WizardMac/ReadStat"
    topics = ("spss", "stata", "sas", "sas7bdat", "readstats")
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
    implements = ["auto_shared_fpic"]
    languages = "C"

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if is_msvc(self):
            self.package_type = "static-library"
            del self.options.shared

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libiconv/1.17")
        self.requires("zlib/[>=1.2.11 <2]")

    def build_requirements(self):
        if not is_msvc(self):
            if self.settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/[>=2.2 <3]")
            self.tool_requires("libtool/2.4.7")
            self.tool_requires("automake/1.16.5")
            # gettext provides AM_ICONV macro used in configure.ac
            self.tool_requires("gettext/0.22.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["release"], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.generate()
            deps = MSBuildDeps(self)
            deps.generate()
        else:
            env = VirtualBuildEnv(self)
            env.generate()

            tc = AutotoolsToolchain(self)
            tc.configure_args.extend([
                "--with-libiconv-prefix={}".format(self.dependencies["libiconv"].package_folder.replace("\\", "/")),])

            # INFO: Ignores Werror when building:
            # readstat_parser.c:6:40: error: a function declaration without a prototype is deprecated in all versions of C
            tc.extra_cflags = ["-Wno-error", "-Wno-strict-prototypes"]
            tc.generate()

            deps = PkgConfigDeps(self)
            deps.generate()

    def _patch_msvc(self):
        vcxproj_file = os.path.join(self.source_folder, "VS17", "ReadStat.vcxproj")
        # Replace the hardcoded platform toolset by the one from the Conan profile
        platform_toolset = MSBuildToolchain(self).toolset
        replace_in_file(self, vcxproj_file,
                "<PlatformToolset>v141</PlatformToolset>",
                f"<PlatformToolset>{platform_toolset}</PlatformToolset>")
        # Remove the hardcoded Windows target platform version, let Conan handle it
        replace_in_file(self, vcxproj_file,
                "<WindowsTargetPlatformVersion>10.0.17763.0</WindowsTargetPlatformVersion>",
                "")
        # Inject the conan generators into the project file, so we can use the dependencies
        import_conan_generators = ""
        for props_file in ["conantoolchain.props", "conandeps.props"]:
            props_path = os.path.join(self.generators_folder, props_file)
            import_conan_generators += f"<Import Project=\"{props_path}\" />"
        replace_in_file(self, vcxproj_file,
                        '<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.targets" />',
                        f'{import_conan_generators}<Import Project="$(VCTargetsPath)\\Microsoft.Cpp.targets" />')

    def build(self):
        self._patch_msvc()
        if is_msvc(self):
            msbuild = MSBuild(self)
            msbuild.build(os.path.join(self.source_folder, "VS17", "ReadStat.sln"), targets=["ReadStat"])
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            verbose = "1" if self.conf.get("tools.compilation:verbosity", check_type=str) == "verbose" else "0"
            autotools.make(args=[f"V={verbose}"])

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            copy(self, "readstat.h", src=os.path.join(self.source_folder, "src"), dst=os.path.join(self.package_folder, "include"))
            copy(self, "*.lib", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "readstat")
        self.cpp_info.libs = ["ReadStat"] if is_msvc(self) else ["readstat"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("m")
