from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    rename,
    rm,
    rmdir,
    replace_in_file
)
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class LibiconvConan(ConanFile):
    name = "libiconv"
    description = "Convert text to and from Unicode"
    license = ("LGPL-2.0-or-later", "LGPL-2.1-or-later")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/libiconv/"
    topics = ("iconv", "text", "encoding", "locale", "unicode", "conversion")

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
    def _is_clang_cl(self):
        return self.settings.compiler == "clang" and self.settings.os == "Windows" and \
               self.settings.compiler.get_safe("runtime")

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
        if Version(self.version) >= "1.17":
            self.license = "LGPL-2.1-or-later"
        else:
            self.license = "LGPL-2.0-or-later"

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
            self.win_bash = True

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            if self.settings.arch == "x86":
                tc.update_configure_args({
                    "--host": "i686-w64-mingw32",
                    "RC": "windres --target=pe-i386",
                    "WINDRES": "windres --target=pe-i386",
                })
            elif self.settings.arch == "x86_64":
                tc.update_configure_args({
                    "--host": "x86_64-w64-mingw32",
                    "RC": "windres --target=pe-x86-64",
                    "WINDRES": "windres --target=pe-x86-64",
                })
        msvc_version = {"Visual Studio": "12", "msvc": "180"}
        if is_msvc(self) and Version(self.settings.compiler.version) >= msvc_version[str(self.settings.compiler)]:
            # https://github.com/conan-io/conan/issues/6514
            tc.extra_cflags.append("-FS")
        if cross_building(self) and is_msvc(self):
            triplet_arch_windows = {"x86_64": "x86_64", "x86": "i686", "armv8": "aarch64"}
            # ICU doesn't like GNU triplet of conan for msvc (see https://github.com/conan-io/conan/issues/12546)
            host_arch = triplet_arch_windows.get(str(self.settings.arch))
            build_arch = triplet_arch_windows.get(str(self._settings_build.arch))

            if host_arch and build_arch:
                host = f"{host_arch}-w64-mingw32"
                build = f"{build_arch}-w64-mingw32"
                tc.configure_args.extend([
                    f"--host={host}",
                    f"--build={build}",
                ])
        env = tc.environment()
        if is_msvc(self) or self._is_clang_cl:
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
        tc.generate(env)

    def _apply_resource_patch(self):
        if self.settings.arch == "x86":
            windres_options_path = os.path.join(self.source_folder, "windows", "windres-options")
            self.output.info("Applying {} resource patch: {}".format(self.settings.arch, windres_options_path))
            replace_in_file(self, windres_options_path, '#   PACKAGE_VERSION_SUBMINOR', '#   PACKAGE_VERSION_SUBMINOR\necho "--target=pe-i386"', strict=True)

    def build(self): 
        apply_conandata_patches(self)
        self._apply_resource_patch()
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING.LIB", self.source_folder, os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        fix_apple_shared_install_name(self)
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
