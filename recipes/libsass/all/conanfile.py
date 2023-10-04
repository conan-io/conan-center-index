from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd, cross_building, stdcpp_library
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, chdir, copy, save, replace_in_file, rmdir, rm
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, MSBuild, MSBuildDeps, MSBuildToolchain, unix_path
import os
import re

required_conan_version = ">=1.54.0"


class LibsassConan(ConanFile):
    name = "libsass"
    license = "MIT"
    homepage = "https://sass-lang.com/libsass"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Libsass is a C/C++ port of the Sass CSS precompiler."
    topics = ("css", "precompiler", "sass")
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

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
        self.tool_requires("libtool/2.4.7")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
        if is_msvc(self):
            self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        autotools_toolchain = AutotoolsToolchain(self)
        autotools_toolchain.configure_args.append(f"--enable-tests=no")
        autotools_toolchain.extra_defines.append(f"LIBSASS_VERSION=\"\\\\\"{self.version}\\\\\"\"")
        autotools_toolchain.generate()
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        if self._is_mingw:
            env = Environment()
            env.define("BUILD", "shared" if self.options.shared else "static")
            env.define("PREFIX", unix_path(self, self.package_folder))
            # Don't force static link to mingw libs, leave this decision to consumer (through LDFLAGS in env)
            env.define("STATIC_ALL", "0")
            env.define("STATIC_LIBGCC", "0")
            env.define("STATIC_LIBSTDCPP", "0")
            env.vars(self).save_script("conanbuild_mingw")
        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    # def _build_visual_studio(self):
    #     with chdir(self, self._source_subfolder):
    #         properties = {
    #             "LIBSASS_STATIC_LIB": "" if self.options.shared else "true",
    #             "WholeProgramOptimization": "true" if any(re.finditer("(^| )[/-]GL($| )", tools.get_env("CFLAGS", ""))) else "false",
    #         }
    #         platforms = {
    #             "x86": "Win32",
    #             "x86_64": "Win64"
    #         }
    #         msbuild = MSBuild(self)
    #         msbuild.build(os.path.join("win", "libsass.sln"), platforms=platforms, properties=properties)

    def build(self):
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        if self._is_mingw:
            replace_in_file(self, os.path.join(self.source_folder, "Makefile"), "CFLAGS   += -O2", "")
            replace_in_file(self, os.path.join(self.source_folder, "Makefile"), "CXXFLAGS += -O2", "")
            replace_in_file(self, os.path.join(self.source_folder, "Makefile"), "LDFLAGS  += -O2", "")
        autotools.make()

    # def _install_mingw(self):
    #     copy(self, "*.h", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))
    #     copy(self, "*.dll", dst="bin", src=os.path.join(self._source_subfolder, "lib"))
    #     copy(self, "*.a", dst="lib", src=os.path.join(self._source_subfolder, "lib"))

    # def _install_visual_studio(self):
    #     self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "include"))
    #     self.copy("*.dll", dst="bin", src=os.path.join(self._source_subfolder, "win", "bin"), keep_path=False)
    #     self.copy("*.lib", dst="lib", src=os.path.join(self._source_subfolder, "win", "bin"), keep_path=False)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["sass"]
        if self.settings.os in ["FreeBSD", "Linux"]:
            self.cpp_info.system_libs.extend(["dl", "m"])
        if not self.options.shared and stdcpp_library(self):
            self.cpp_info.system_libs.append(stdcpp_library(self))
