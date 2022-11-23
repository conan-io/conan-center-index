from conan import ConanFile
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    rename,
    replace_in_file,
    rm,
    rmdir
)
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class LibiconvConan(ConanFile):
    name = "libiconv"
    description = "Convert text to and from Unicode"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/libiconv/"
    topics = ("iconv", "text", "encoding", "locale", "unicode", "conversion")
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
    def _is_clang_cl(self):
        return (self.settings.compiler == "clang" and self.settings.os == "Windows") \
               or self.settings.get_safe("compiler.toolset") == "ClangCL"

    @property
    def _msvc_tools(self):
        return ("clang-cl", "llvm-lib", "lld-link") if self._is_clang_cl else ("cl", "lib", "link")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

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
        if self._settings_build.os == "Windows":
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
            self.win_bash = True

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        def requires_fs_flag():
            # See https://github.com/conan-io/conan/issues/11158
            return (self.settings.compiler == "Visual Studio" and Version(self.settings.compiler.version) >= "12") or \
                    (self.settings.compiler == "msvc" and Version(self.settings.compiler.version) >= "180")

        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if requires_fs_flag():
            # order of setting flags and environment vars is important
            # See https://github.com/conan-io/conan/issues/12228
            tc.extra_cflags.append("-FS")
        tc.generate()

        if is_msvc(self) or self._is_clang_cl:
            env = Environment()
            cc, lib, link = self._msvc_tools
            build_aux_path = os.path.join(self.source_folder, "build-aux")
            lt_compile = unix_path(self, os.path.join(build_aux_path, "compile"))
            lt_ar = unix_path(self, os.path.join(build_aux_path, "ar-lib"))
            env.define("CC", f"{lt_compile} {cc} -nologo")
            env.define("CXX", f"{lt_compile} {cc} -nologo")
            env.define("LD", link)
            env.define("STRIP", ":")
            env.define("AR", f"{lt_ar} {lib}")
            env.define("RANLIB", ":")
            env.define("NM", "dumpbin -symbols")
            env.define("win32_target", "_WIN32_WINNT_VISTA")
            env.vars(self).save_script("conanbuild_libiconv_msvc")

    def _patch_sources(self):
        apply_conandata_patches(self)
        # relocatable shared libs on macOS
        for configure in ["configure", os.path.join("libcharset", "configure")]:
            replace_in_file(self, os.path.join(self.source_folder, configure),
                                  "-install_name \\$rpath/", "-install_name @rpath/")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING.LIB", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        if (is_msvc(self) or self._is_clang_cl) and self.options.shared:
            for import_lib in ["iconv", "charset"]:
                rename(self, os.path.join(self.package_folder, "lib", f"{import_lib}.dll.lib"),
                             os.path.join(self.package_folder, "lib", f"{import_lib}.lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "Iconv")
        self.cpp_info.set_property("cmake_target_name", "Iconv::Iconv")
        self.cpp_info.libs = ["iconv", "charset"]

        # TODO: to remove in conan v2
        self.cpp_info.names["cmake_find_package"] = "Iconv"
        self.cpp_info.names["cmake_find_package_multi"] = "Iconv"
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
