from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, MSBuild, MSBuildToolchain
import os

required_conan_version = ">=1.54.0"


class LibmicrohttpdConan(ConanFile):
    name = "libmicrohttpd"
    description = "A small C library that is supposed to make it easy to run an HTTP server"
    homepage = "https://www.gnu.org/software/libmicrohttpd/"
    topics = ("httpd", "server", "service")
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_https": [True, False],
        "with_error_messages": [True, False],
        "with_postprocessor": [True, False],
        "with_digest_authentification": [True, False],
        "epoll": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_https": False,  # FIXME: should be True, but gnutls is not yet available in cci
        "with_error_messages": True,
        "with_postprocessor": True,
        "with_digest_authentification": True,
        "epoll": True,
        "with_zlib": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Linux":
            del self.options.epoll
        if is_msvc(self):
            del self.options.with_https
            del self.options.with_error_messages
            del self.options.with_postprocessor
            del self.options.with_digest_authentification
            del self.options.with_zlib

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_zlib"):
            self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        if is_msvc(self) and self.settings.arch not in ("x86", "x86_64"):
            raise ConanInvalidConfiguration("Unsupported architecture (only x86 and x86_64 are supported)")
        if self.options.get_safe("with_https"):
            raise ConanInvalidConfiguration("gnutls is not (yet) available in cci")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not is_msvc(self):
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = MSBuildToolchain(self)
            tc.configuration = self._msvc_configuration
            tc.properties["WholeProgramOptimization"] = "false"
            tc.generate()
        else:
            VirtualBuildEnv(self).generate()
            if not cross_building(self):
                VirtualRunEnv(self).generate(scope="build")
            tc = AutotoolsToolchain(self)
            yes_no = lambda v: "yes" if v else "no"
            tc.configure_args.extend([
                f"--enable-shared={yes_no(self.options.shared)}",
                f"--enable-static={yes_no(not self.options.shared)}",
                f"--enable-https={yes_no(self.options.with_https)}",
                f"--enable-messages={yes_no(self.options.with_error_messages)}",
                f"--enable-postprocessor={yes_no(self.options.with_postprocessor)}",
                f"--enable-dauth={yes_no(self.options.with_digest_authentification)}",
                f"--enable-epoll={yes_no(self.options.get_safe('epoll'))}",
                "--disable-doc",
                "--disable-examples",
                "--disable-curl",
            ])
            tc.generate()
            AutotoolsDeps(self).generate()

    @property
    def _msvc_configuration(self):
        prefix = "Debug" if self.settings.build_type == "Debug" else "Release"
        suffix = "dll" if self.options.shared else "static"
        return f"{prefix}-{suffix}"

    @property
    def _msvc_sln_folder(self):
        # TODO: use VS-Any-Version folder once https://github.com/conan-io/conan/pull/12817 available in conan client
        return os.path.join(self.source_folder, "w32", "VS2022")

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            #==============================
            # TODO: to remove once https://github.com/conan-io/conan/pull/12817 available in conan client
            vcxproj_file = os.path.join(self._msvc_sln_folder, "libmicrohttpd.vcxproj")
            replace_in_file(
                self, vcxproj_file,
                "<WholeProgramOptimization Condition=\"! $(Configuration.StartsWith('Debug'))\">true</WholeProgramOptimization>",
                "",
            )
            toolset = MSBuildToolchain(self).toolset
            replace_in_file(
                self, vcxproj_file,
                "<PlatformToolset>v143</PlatformToolset>",
                f"<PlatformToolset>{toolset}</PlatformToolset>",
            )
            conantoolchain_props = os.path.join(self.generators_folder, MSBuildToolchain.filename)
            replace_in_file(
                self, vcxproj_file,
                "<Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
                f"<Import Project=\"{conantoolchain_props}\" /><Import Project=\"$(VCTargetsPath)\\Microsoft.Cpp.targets\" />",
            )
            #==============================

            msbuild = MSBuild(self)
            msbuild.build_type = self._msvc_configuration
            msbuild.platform = "Win32" if self.settings.arch == "x86" else msbuild.platform
            msbuild.build(sln=os.path.join(self._msvc_sln_folder, "libmicrohttpd.sln"), targets=["libmicrohttpd"])
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            output_dir = os.path.join(self._msvc_sln_folder, "Output")
            copy(self, "*.lib", src=output_dir, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.dll", src=output_dir, dst=os.path.join(self.package_folder, "bin"), keep_path=False)
            copy(self, "*.h", src=output_dir, dst=os.path.join(self.package_folder, "include"), keep_path=False)
        else:
            autotools = Autotools(self)
            autotools.install()
            rm(self, "*.la", os.path.join(self.package_folder, "lib"))
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libmicrohttpd")
        libname = "microhttpd"
        if is_msvc(self):
            libname = "libmicrohttpd"
            if self.options.shared:
                libname += "-dll"
            if self.settings.build_type == "Debug":
                libname += "_d"
        self.cpp_info.libs = [libname]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.defines.append("MHD_W32DLL")
            self.cpp_info.system_libs = ["ws2_32"]
