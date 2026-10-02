from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import copy, get, rename, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc, unix_path
import os

required_conan_version = ">=2.4"


class SpeexDSPConan(ConanFile):
    name = "speexdsp"
    description = "SpeexDSP is a patent-free, Open Source/Free Software DSP library providing resampler, echo cancellation, noise suppression, and other audio processing functions."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xiph/speexdsp"
    topics = ("audio", "dsp", "resampler", "echo-cancellation", "noise-suppression")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "fixed_point": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "fixed_point": False,
    }
    implements = ["auto_shared_fpic"]
    languages = "C"

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self.settings_build.os == "Windows":
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
        yes_no = lambda v: "yes" if v else "no"
        tc.configure_args.extend([
            f"--enable-fixed-point={yes_no(self.options.fixed_point)}",
            "--disable-examples",
        ])
        if is_msvc(self):
            if check_min_vs(self, "180", raise_invalid=False):
                tc.extra_cflags.append("-FS")
        tc.generate()

        if is_msvc(self):
            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            ar_wrapper = unix_path(self, automake_conf.get("user.automake:lib-wrapper", check_type=str))
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f'{ar_wrapper} "lib -nologo"')
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        autotools = Autotools(self)
        autotools.install()

        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        fix_apple_shared_install_name(self)

        if is_msvc(self) and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "speexdsp.dll.lib"),
                         os.path.join(self.package_folder, "lib", "speexdsp.lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SpeexDSP")
        self.cpp_info.set_property("cmake_target_name", "SpeexDSP::speexdsp")
        self.cpp_info.set_property("pkg_config_name", "speexdsp")
        self.cpp_info.libs = ["speexdsp"]
        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.cpp_info.system_libs.append("m")
