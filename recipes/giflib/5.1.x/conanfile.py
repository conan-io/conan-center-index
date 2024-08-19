import os
import shutil

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import chdir, copy, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

required_conan_version = ">=1.53.0"


class GiflibConan(ConanFile):
    name = "giflib"
    description = "A library and utilities for reading and writing GIF images."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://giflib.sourceforge.net"
    topics = ("image", "multimedia", "format", "graphics")

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
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        # The exported files I took them from
        # https://github.com/bjornblissing/osg-3rdparty-cmake/tree/master/giflib
        # refactored a little
        copy(self, "unistd.h", src=self.recipe_folder, dst=self.export_sources_folder)
        copy(self, "gif_lib.h", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if not is_msvc(self):
            self.tool_requires("gnu-config/cci.20210814")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
            if is_msvc(self):
                self.tool_requires("automake/1.16.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")
        tc = AutotoolsToolchain(self)
        if is_msvc(self):
            tc.extra_defines.append("USE_GIF_DLL" if self.options.shared else "USE_GIF_LIB")
            tc.extra_cflags.append("-FS")
        tc.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            # ar-lib wrapper is added by ./configure automatically
            # env.define("AR", f'{ar_wrapper} "lib -nologo"')
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def _patch_sources(self):
        # disable util build - tools and internal libs
        replace_in_file(self, os.path.join(self.source_folder, "Makefile.in"),
                        "SUBDIRS = lib util pic $(am__append_1)",
                        "SUBDIRS = lib pic $(am__append_1)")

        if is_msvc(self):
            # add unistd.h for VS
            shutil.copy(os.path.join(self.export_sources_folder, "unistd.h"),
                        os.path.join(self.source_folder, "lib"))
            # fully replace gif_lib.h for VS, with patched version
            ver_components = self.version.split(".")
            header_path = os.path.join(self.source_folder, "lib", "gif_lib.h")
            shutil.copy(os.path.join(self.export_sources_folder, "gif_lib.h"), header_path)
            replace_in_file(self, header_path, "@GIFLIB_MAJOR@", ver_components[0])
            replace_in_file(self, header_path, "@GIFLIB_MINOR@", ver_components[1])
            replace_in_file(self, header_path, "@GIFLIB_RELEASE@", ver_components[2])
        for gnu_config in [
            self.conf.get("user.gnu-config:config_guess", check_type=str),
            self.conf.get("user.gnu-config:config_sub", check_type=str)
        ]:
            if gnu_config:
                copy(self, os.path.basename(gnu_config), src=os.path.dirname(gnu_config), dst=self.source_folder)
        if is_apple_os(self):
            # relocatable shared lib on macOS
            replace_in_file(self, os.path.join(self.source_folder, "configure"),
                            "-install_name \\$rpath/\\$soname",
                            "-install_name \\@rpath/\\$soname")

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()
        copy(self, "COPYING*",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder, keep_path=False)
        rm(self, "*.la", self.package_folder, recursive=True)
        rmdir(self, os.path.join(self.package_folder, "share"))
        if is_msvc(self) and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "gif.dll.lib"),
                         os.path.join(self.package_folder, "lib", "gif.lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "GIF")
        self.cpp_info.set_property("cmake_target_name", "GIF::GIF")

        self.cpp_info.libs = ["gif"]
        if is_msvc(self):
            self.cpp_info.defines.append("USE_GIF_DLL" if self.options.shared else "USE_GIF_LIB")

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "GIF"
        self.cpp_info.names["cmake_find_package_multi"] = "GIF"
