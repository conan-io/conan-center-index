from conan import ConanFile
from conan.tools.build import stdcpp_library
from conan.tools.files import chdir, copy, get, replace_in_file, rm, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import MSBuild, MSBuildToolchain, is_msvc
import os
import re

required_conan_version = ">=1.53.0"


class LibsassConan(ConanFile):
    name = "libsass"
    description = "A C/C++ implementation of a Sass compiler"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "libsass.org"
    topics = ("Sass", "compiler")

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

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self.settings.os != "Windows":
            self.tool_requires("libtool/2.4.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _msbuild_configuration(self):
        return "Debug" if self.settings.build_type == "Debug" else "Release"

    def generate(self):
        if not is_msvc(self):
            tc = AutotoolsToolchain(self)
            tc.configure_args += ["--disable-tests"]
            env = tc.environment()
            if self._is_mingw:
                env.define("BUILD", "shared" if self.options.shared else "static")
                # Don't force static link to mingw libs, leave this decision to consumer (through LDFLAGS in env)
                env.define("STATIC_ALL", "0")
                env.define("STATIC_LIBGCC", "0")
                env.define("STATIC_LIBSTDCPP", "0")
            tc.generate(env)
        else:
            with chdir(self, self.source_folder):
                tc = MSBuildToolchain(self)
                tc.configuration = self._msbuild_configuration
                tc.platform = "Win32" if self.settings.arch == "x86" else "Win64"
                tc.properties["LIBSASS_STATIC_LIB"] = "" if self.options.shared else "true"
                wpo_enabled = any(re.finditer("(^| )[/-]GL($| )", os.environ.get("CFLAGS", "")))
                tc.properties["WholeProgramOptimization"] = "true" if wpo_enabled else "false"
                tc.generate()

    def _patch_sources(self):
        if is_msvc(self):
            # TODO: to remove once https://github.com/conan-io/conan/pull/12817 available in conan client
            platform_toolset = MSBuildToolchain(self).toolset
            import_conan_generators = ""
            for props_file in ["conantoolchain.props", "conandeps.props"]:
                props_path = os.path.join(self.generators_folder, props_file)
                if os.path.exists(props_path):
                    import_conan_generators += f'<Import Project="{props_path}" />'
            vcxproj_file = os.path.join(self.source_folder, "win", "libsass.vcxproj")
            for exiting_toolset in ["v120", "v140", "v141", "v142", "v143"]:
                replace_in_file(self, vcxproj_file,
                                f"<PlatformToolset>{exiting_toolset}</PlatformToolset>",
                                f"<PlatformToolset>{platform_toolset}</PlatformToolset>", strict=False)
            # Inject VS 2022 support
            replace_in_file(self, vcxproj_file,
                            '<PropertyGroup Label="VS2019',
                            ('<PropertyGroup Label="VS2022 toolset selection" Condition="\'$(VisualStudioVersion)\' == \'17.0\'">\n'
                             f'  <PlatformToolset>{platform_toolset}</PlatformToolset>\n'
                             '</PropertyGroup>\n'
                             '<PropertyGroup Label="VS2019'))
            if props_path:
                replace_in_file(self, vcxproj_file,
                                'msbuild/2003">',
                                f'msbuild/2003">\n{import_conan_generators}')
        else:
            makefile = os.path.join(self.source_folder, "Makefile")
            replace_in_file(self, makefile, "+= -O2", "+=")

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            if is_msvc(self):
                msbuild = MSBuild(self)
                msbuild.build_type = self._msbuild_configuration
                msbuild.platform = "Win32" if self.settings.arch == "x86" else "Win64"
                msbuild.build(sln=os.path.join("win", "libsass.sln"))
            else:
                save(self, path="VERSION", content=f"{self.version}")
                autotools = Autotools(self)
                autotools.autoreconf()
                autotools.configure()
                autotools.make()

    def _install_autotools(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", self.package_folder, recursive=True)

    def _install_mingw(self):
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))
        copy(self, "*.dll",
             dst=os.path.join(self.package_folder, "bin"),
             src=os.path.join(self.source_folder, "lib"))
        copy(self, "*.a",
             dst=os.path.join(self.package_folder, "lib"),
             src=os.path.join(self.source_folder, "lib"))

    def _install_msvc(self):
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))
        copy(self, "*.dll",
             dst=os.path.join(self.package_folder, "bin"),
             src=os.path.join(self.source_folder, "win", "bin"),
             keep_path=False)
        copy(self, "*.lib",
             dst=os.path.join(self.package_folder, "lib"),
             src=os.path.join(self.source_folder, "win", "bin"),
             keep_path=False)

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        if self._is_mingw:
            self._install_mingw()
        elif is_msvc(self):
            self._install_msvc()
        else:
            self._install_autotools()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libsass")
        self.cpp_info.libs = ["libsass" if is_msvc(self) else "sass"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m"])
        if not self.options.shared and stdcpp_library(self):
            self.cpp_info.system_libs.append(stdcpp_library(self))
