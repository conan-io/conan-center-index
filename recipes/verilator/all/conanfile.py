import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.env import Environment, VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path
from conan.tools.scm import Version

required_conan_version = ">=1.60.0 <2.0 || >=2.0.6"


class VerilatorConan(ConanFile):
    name = "verilator"
    description = "Verilator compiles synthesizable Verilog and Synthesis assertions into single- or multi-threaded C++ or SystemC code"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.veripool.org/wiki/verilator"
    topics = ("verilog", "hdl", "eda", "simulator", "hardware", "fpga", "pre-built")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("strawberryperl/5.32.1.1", visible=False)
            if self._needs_old_bison:
                # don't upgrade to bison 3.7.0 or above, or it fails to build
                # because of https://github.com/verilator/verilator/pull/2505
                self.requires("winflexbison/2.5.22", visible=False)
            else:
                self.requires("winflexbison/2.5.25", visible=False)
        else:
            self.requires("flex/2.6.4", visible=False)
        if is_msvc(self):
            self.requires("dirent/1.24", visible=False)

    def package_id(self):
        # Verilator is an executable-only package, so the compiler does not matter
        del self.info.settings.compiler

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross building is not yet supported. Contributions are welcome")

        if (
            Version(self.version) >= "4.200"
            and self.settings.compiler == "gcc"
            and Version(self.settings.compiler.version) < "7"
        ):
            raise ConanInvalidConfiguration("GCC < version 7 is not supported")

        if self.settings.os == "Windows" and Version(self.version) >= "4.200":
            raise ConanInvalidConfiguration("Windows build is not yet supported. Contributions are welcome")

    @property
    def _needs_old_bison(self):
        return Version(self.version) < "4.100"

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
            self.tool_requires("automake/1.16.5")
            self.tool_requires("winflexbison/<host_version>")
            self.tool_requires("strawberryperl/<host_version>")
        else:
            self.tool_requires("flex/<host_version>")
            if self._needs_old_bison:
                # don't upgrade to bison 3.7.0 or above, or it fails to build
                # because of https://github.com/verilator/verilator/pull/2505
                self.tool_requires("bison/3.5.3")
            else:
                self.tool_requires("bison/3.8.2")
        if Version(self.version) >= "4.224":
            self.tool_requires("autoconf/2.71")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

        tc = AutotoolsToolchain(self)
        if self.settings.get_safe("compiler.libcxx") == "libc++":
            tc.extra_cxxflags.append("-lc++")
        if is_msvc(self):
            tc.extra_cxxflags.append("-EHsc")
            tc.extra_cxxflags.append("-FS")
            tc.defines.append("YY_NO_UNISTD_H")
        tc.configure_args += ["--datarootdir=${prefix}/bin/share"]
        flex = "flex" if self.settings.os != "Windows" else "winflexbison"
        tc.extra_cxxflags += [f"-I{unix_path(self, self.dependencies[flex].cpp_info.includedir)}"]
        tc.extra_ldflags += [f"-L{unix_path(self, self.dependencies[flex].cpp_info.libdir)}"]
        tc.generate()

        tc.make_args += [
            "CFG_WITH_DEFENV=false",
            "SRC_TARGET={}".format("dbg" if self.settings.build_type == "Debug" else "opt")
        ]
        if self.settings.build_type == "Debug":
            tc.make_args.append("DEBUG=1")
        if is_msvc(self):
            msvc_link_sh_path = unix_path(self, os.path.join(self.source_folder, "msvc_link.sh"))
            tc.make_args.append(f"PROGLINK={msvc_link_sh_path}")

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

    def _patch_sources(self):
        if Version(self.version) < "4.200":
            apply_conandata_patches(self)
        rm(self, "config_build.h", os.path.join(self.source_folder, "src", "config_build.h"))
        if is_msvc(self):
            replace_in_file(self, os.path.join(self.source_folder, "src", "Makefile_obj.in"),
                            "${LINK}", "${PROGLINK}")

    def build(self):
        self._patch_sources()
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            if Version(self.version) >= "4.224":
                self.run("autoconf")
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.install()

        share_dir = os.path.join(self.package_folder, "bin", "share")
        share_verilator_dir = os.path.join(share_dir, "verilator")
        rmdir(self, os.path.join(share_dir, "man"))
        rmdir(self, os.path.join(share_dir, "pkgconfig"))
        rmdir(self, os.path.join(share_verilator_dir, "examples"))
        os.unlink(os.path.join(share_verilator_dir, "verilator-config-version.cmake"))
        rename(self, os.path.join(share_verilator_dir, "verilator-config.cmake"),
                     os.path.join(share_verilator_dir, "verilator-tools.cmake"))
        replace_in_file(self, os.path.join(share_verilator_dir, "verilator-tools.cmake"),
                        "${CMAKE_CURRENT_LIST_DIR}", "${CMAKE_CURRENT_LIST_DIR}/../../..")
        if self.settings.build_type == "Debug":
            replace_in_file(self, os.path.join(share_verilator_dir, "verilator-tools.cmake"),
                            "verilator_bin", "verilator_bin_dbg")
        shutil.move(os.path.join(share_verilator_dir, "include"), self.package_folder)
        if Version(self.version) >= "4.224":
            shutil.move(os.path.join(share_verilator_dir, "bin", "verilator_ccache_report"),
                        os.path.join(self.package_folder, "bin", "verilator_ccache_report"))
        shutil.move(os.path.join(share_verilator_dir, "bin", "verilator_includer"),
                    os.path.join(self.package_folder, "bin", "verilator_includer"))
        rmdir(self, os.path.join(share_verilator_dir, "bin"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        bindir = os.path.join(self.package_folder, "bin")
        verilator_bin = "verilator_bin_dbg" if self.settings.build_type == "Debug" else "verilator_bin"
        self.conf_info.define("user.verilator:verilator", verilator_bin)

        module_path = os.path.join("bin", "share", "verilator", "verilator-tools.cmake")
        self.cpp_info.set_property("cmake_build_modules", [module_path])

        # TODO: Legacy, to be removed on Conan 2.0
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
        self.output.info(f"Setting VERILATOR_BIN environment variable to {verilator_bin}")
        self.env_info.VERILATOR_BIN = verilator_bin
        self.output.info(f"Setting VERILATOR_ROOT environment variable to {self.package_folder}")
        self.env_info.VERILATOR_ROOT = self.package_folder
        self.cpp_info.builddirs.append(os.path.join("bin", "share", "verilator"))
        self.cpp_info.build_modules["cmake_find_package"].append(module_path)
        self.cpp_info.build_modules["cmake_find_package_multi"].append(module_path)
