from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path
import os

required_conan_version = ">=1.54.0"


class OpencoreAmrConan(ConanFile):
    name = "opencore-amr"
    homepage = "https://sourceforge.net/projects/opencore-amr/"
    description = "OpenCORE Adaptive Multi Rate (AMR) speech codec library implementation."
    topics = ("audio-codec", "amr", "opencore")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
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

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
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
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--disable-compile-c",
            "--disable-examples",
        ])
        if is_msvc(self):
            tc.extra_cxxflags.append("-EHsc")
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cxxflags.append("-FS")
        tc.generate()

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

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        fix_apple_shared_install_name(self)

        if is_msvc(self) and self.options.shared:
            for lib in ("opencore-amrwb", "opencore-amrnb"):
                rename(self, os.path.join(self.package_folder, "lib", "{}.dll.lib".format(lib)),
                             os.path.join(self.package_folder, "lib", "{}.lib".format(lib)))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "opencore-amr")
        self.cpp_info.set_property(
            "cmake_target_name", "opencore-amr::opencore-amr")
        for lib in ("opencore-amrwb", "opencore-amrnb"):
            self.cpp_info.components[lib].set_property(
                "cmake_target_name", f'opencore-amr::{lib}')
            self.cpp_info.components[lib].set_property("pkg_config_name", lib)
            self.cpp_info.components[lib].libs = [lib]
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components[lib].system_libs.extend(["m"])

            # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generator removed
            self.cpp_info.components[lib].names["pkg_config"] = lib
