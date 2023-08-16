from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path
import os

required_conan_version = ">=1.57.0"


class GslConan(ConanFile):
    name = "gsl"
    description = "GNU Scientific Library"
    homepage = "https://www.gnu.org/software/gsl"
    topics = ("numerical", "math", "random", "scientific")
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-3.0-or-later"

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
        self.tool_requires("libtool/2.4.7")
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()

        tc = AutotoolsToolchain(self)
        if self.settings.os == "Windows":
            tc.extra_defines.extend(["HAVE_WIN_IEEE_INTERFACE", "WIN32"])
            if self.options.shared:
                tc.extra_defines.append("GSL_DLL")
        if self.settings.os == "Linux" and "x86" in self.settings.arch:
            tc.extra_defines.append("HAVE_GNUX86_IEEE_INTERFACE")
        if is_msvc(self):
            tc.configure_args.extend([
                "ac_cv_func_memcpy=yes",
                "ac_cv_func_memmove=yes",
                "ac_cv_c_c99inline=no",
            ])
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cflags.append("-FS")
        env = tc.environment()
        if is_msvc(self):
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
        tc.generate(env)

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.c", os.path.join(self.package_folder, "include", "gsl"))
        rm(self, "gsl-config", os.path.join(self.package_folder, "bin"))
        fix_apple_shared_install_name(self)
        if is_msvc(self) and self.options.shared:
            pjoin = lambda p: os.path.join(self.package_folder, "lib", p)
            rename(self, pjoin("gsl.dll.lib"), pjoin("gsl.lib"))
            rename(self, pjoin("gslcblas.dll.lib"), pjoin("gslcblas.lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "GSL")
        self.cpp_info.set_property("cmake_target_name", "GSL::gsl")
        self.cpp_info.set_property("pkg_config_name", "gsl")

        self.cpp_info.components["libgsl"].set_property("cmake_target_name", "GSL::gsl")
        self.cpp_info.components["libgsl"].libs = ["gsl"]
        self.cpp_info.components["libgsl"].requires = ["libgslcblas"]

        self.cpp_info.components["libgslcblas"].set_property("cmake_target_name", "GSL::gslcblas")
        self.cpp_info.components["libgslcblas"].libs = ["gslcblas"]

        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.components["libgsl"].system_libs = ["m"]
            self.cpp_info.components["libgslcblas"].system_libs = ["m"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "GSL"
        self.cpp_info.names["cmake_find_package_multi"] = "GSL"
        self.cpp_info.components["libgsl"].names["cmake_find_package"] = "gsl"
        self.cpp_info.components["libgsl"].names["cmake_find_package_multi"] = "gsl"
        self.cpp_info.components["libgslcblas"].names["cmake_find_package"] = "gslcblas"
        self.cpp_info.components["libgslcblas"].names["cmake_find_package_multi"] = "gslcblas"
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
