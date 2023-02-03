from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, MSBuild, MSBuildDeps, MSBuildToolchain
import os

required_conan_version = ">=1.54.0"


class OpusFileConan(ConanFile):
    name = "opusfile"
    description = "stand-alone decoder library for .opus streams"
    topics = ("opus", "opusfile", "audio", "decoder", "decoding", "multimedia", "sound")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/opusfile"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "http": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "http": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _msbuild_configuration(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("ogg/1.3.5")
        self.requires("opus/1.3.1")
        if self.options.http:
            self.requires("openssl/1.1.1s")

    def validate(self):
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support building as shared with Visual Studio")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("libtool/2.4.7")
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/1.9.3")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.configuration = self._msbuild_configuration
            tc.properties["WholeProgramOptimization"] = "false"
            tc.generate()
            deps = MSBuildDeps(self)
            deps.configuration = self._msbuild_configuration
            deps.generate()
        else:
            VirtualBuildEnv(self).generate()
            tc = AutotoolsToolchain(self)
            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.extend([
                f"--enable-http={yes_no(self.options.http)}",
                "--disable-examples",
            ])
            tc.generate()
            PkgConfigDeps(self).generate()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            sln_folder = os.path.join(self.source_folder, "win32", "VS2015")
            vcxproj = os.path.join(sln_folder, "opusfile.vcxproj")
            if not self.options.http:
                replace_in_file(self, vcxproj, "OP_ENABLE_HTTP;", "")

            #==============================
            # TODO: to remove once https://github.com/conan-io/conan/pull/12817 available in conan client
            replace_in_file(
                self, vcxproj,
                "<WholeProgramOptimization>true</WholeProgramOptimization>",
                "",
            )
            replace_in_file(
                self, vcxproj,
                "<PlatformToolset>v140</PlatformToolset>",
                f"<PlatformToolset>{MSBuildToolchain(self).toolset}</PlatformToolset>",
            )
            import_conan_generators = ""
            for props_file in [MSBuildToolchain.filename, "conandeps.props"]:
                props_path = os.path.join(self.generators_folder, props_file)
                if os.path.exists(props_path):
                    import_conan_generators += f"<Import Project=\"{props_path}\" />"
            replace_in_file(
                self, vcxproj,
                "<Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
                f"{import_conan_generators}<Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
            )
            #==============================

            msbuild = MSBuild(self)
            msbuild.build_type = self._msbuild_configuration
            msbuild.platform = "Win32" if self.settings.arch == "x86" else msbuild.platform
            msbuild.build(os.path.join(sln_folder, "opusfile.sln"), targets=["opusfile"])
        else:
            autotools = Autotools(self)
            autotools.autoreconf()
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            include_folder = os.path.join(self.source_folder, "include")
            copy(self, "*", src=include_folder, dst=os.path.join(self.package_folder, "include", "opus"))
            copy(self, "*.dll", src=self.source_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            copy(self, "*.lib", src=self.source_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "share"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.components["libopusfile"].set_property("pkg_config_name", "opusfile")
        self.cpp_info.components["libopusfile"].libs = ["opusfile"]
        self.cpp_info.components["libopusfile"].includedirs.append(os.path.join("include", "opus"))
        self.cpp_info.components["libopusfile"].requires = ["ogg::ogg", "opus::opus"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["libopusfile"].system_libs = ["m", "dl", "pthread"]

        if is_msvc(self):
            if self.options.http:
                self.cpp_info.components["libopusfile"].requires.append("openssl::openssl")
        else:
            self.cpp_info.set_property("pkg_config_name", "opusfile-do-not-use")
            self.cpp_info.components["opusurl"].set_property("pkg_config_name", "opusurl")
            self.cpp_info.components["opusurl"].libs = ["opusurl"]
            self.cpp_info.components["opusurl"].requires = ["libopusfile"]
            if self.options.http:
                self.cpp_info.components["opusurl"].requires.append("openssl::openssl")
