from conan import ConanFile
from conan.tools.files import get, rmdir, patch, replace_in_file, rename
from conan.tools.build import cross_building
from conan.tools.scm   import Version
from conans import AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import os
import shutil

required_conan_version = ">=1.47.0"

class VerilatorConan(ConanFile):
    name = "verilator"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.veripool.org/wiki/verilator"
    description = "Verilator compiles synthesizable Verilog and Synthesis assertions into single- or multithreaded C++ or SystemC code"
    topics = ("verilog", "hdl", "eda", "simulator", "hardware", "fpga")

    settings = "os", "arch", "compiler", "build_type"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])
            
    @property
    def _needs_old_bison(self):
        return Version(self.version) < "4.100"

    def build_requirements(self):
        if self._settings_build.os == "Windows" and "CONAN_BASH_PATH" not in os.environ:
            if self.settings.compiler == "Visual Studio":
                self.build_requires("msys2/cci.latest")
                self.build_requires("automake/1.16.4")
            if self._needs_old_bison:
                # don't upgrade to bison 3.7.0 or above, or it fails to build
                # because of https://github.com/verilator/verilator/pull/2505
                self.build_requires("winflexbison/2.5.22")
            else:
                self.build_requires("winflexbison/2.5.24")
            self.build_requires("strawberryperl/5.30.0.1")
        else:
            self.build_requires("flex/2.6.4")
            if self._needs_old_bison:
                # don't upgrade to bison 3.7.0 or above, or it fails to build
                # because of https://github.com/verilator/verilator/pull/2505
                self.build_requires("bison/3.5.3")
            else:
                self.build_requires("bison/3.7.6")
        if Version(self.version) >= "4.224":
            self.build_requires("autoconf/2.71")


    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("strawberryperl/5.30.0.1")
        if self.settings.compiler == "Visual Studio":
            self.requires("dirent/1.23.2", private=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross building is not yet supported. Contributions are welcome")

        if Version(self.version) >= "4.200" and self.settings.compiler == "gcc" and Version(self.settings.compiler.version) < "7":
            raise ConanInvalidConfiguration("GCC < version 7 is not supported")
        
        if self.settings.os == "Windows" and Version(self.version) >= "4.200":
            raise ConanInvalidConfiguration("Windows build is not yet supported. Contributions are welcome")
    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            build_env = {
                "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
            }
            with tools.vcvars(self.settings):
                with tools.environment_append(build_env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        self._autotools.library_paths = []
        if self.settings.get_safe("compiler.libcxx") == "libc++":
            self._autotools.libs.append("c++")
        if self.settings.compiler == "Visual Studio":
            self._autotools.cxx_flags.append("-EHsc")
            self._autotools.defines.append("YY_NO_UNISTD_H")
            self._autotools.flags.append("-FS")
        conf_args = [
            "--datarootdir={}/bin/share".format(tools.unix_path(self.package_folder)),
        ]
        yacc = tools.get_env("YACC")
        if yacc:
            if yacc.endswith(" -y"):
                yacc = yacc[:-3]
        with tools.environment_append({"YACC": yacc}):
            if Version(self.version) >= "4.224":
               with tools.chdir(self._source_subfolder):
                    self.run("autoconf", win_bash=tools.os_info.is_windows, run_environment=True)
            self._autotools.configure(args=conf_args, configure_dir=os.path.join(self.build_folder, self._source_subfolder))

        return self._autotools

    @property
    def _make_args(self):
        args = [
            "CFG_WITH_DEFENV=false",
            "SRC_TARGET={}".format("dbg" if self.settings.build_type == "Debug" else "opt"),
        ]
        if self.settings.build_type == "Debug":
            args.append("DEBUG=1")
        if self.settings.compiler == "Visual Studio":
            args.append("PROGLINK={}".format(tools.unix_path(os.path.join(self.build_folder, self._source_subfolder, "msvc_link.sh"))))
        return args

    def _patch_sources(self):
        if Version(self.version) < "4.200":
            for patch_file in self.conan_data.get("patches", {}).get(self.version, []):
                patch(self, **patch_file)
        try:
            os.unlink(os.path.join(self._source_subfolder, "src", "config_build.h"))
        except FileNotFoundError:
            pass

        if self.settings.compiler == "Visual Studio":
            replace_in_file(self, os.path.join(self._source_subfolder, "src", "Makefile_obj.in"),
                                  "${LINK}", "${PROGLINK}")

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make(args=self._make_args)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install(args=self._make_args)

        rmdir(self, os.path.join(self.package_folder, "bin", "share", "man"))
        rmdir(self, os.path.join(self.package_folder, "bin", "share", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "bin", "share", "verilator", "examples"))
        os.unlink(os.path.join(self.package_folder, "bin", "share", "verilator", "verilator-config-version.cmake"))
        rename(self, os.path.join(self.package_folder, "bin", "share", "verilator", "verilator-config.cmake"),
                     os.path.join(self.package_folder, "bin", "share", "verilator", "verilator-tools.cmake"))
        replace_in_file(self, os.path.join(self.package_folder, "bin", "share", "verilator", "verilator-tools.cmake"), 
                            "${CMAKE_CURRENT_LIST_DIR}", "${CMAKE_CURRENT_LIST_DIR}/../../..")
        if self.settings.build_type == "Debug":
            replace_in_file(self, os.path.join(self.package_folder, "bin", "share", "verilator", "verilator-tools.cmake"),
                                 "verilator_bin", "verilator_bin_dbg")

        shutil.move(os.path.join(self.package_folder, "bin", "share", "verilator", "include"), 
                    os.path.join(self.package_folder))

        if Version(self.version) >= "4.224":
            shutil.move(os.path.join(self.package_folder, "bin", "share", "verilator", "bin", "verilator_ccache_report"), 
                    os.path.join(self.package_folder, "bin", "verilator_ccache_report"))

        shutil.move(os.path.join(self.package_folder, "bin", "share", "verilator", "bin", "verilator_includer"), 
                    os.path.join(self.package_folder, "bin", "verilator_includer"))

        rmdir(self, os.path.join(self.package_folder, "bin", "share", "verilator", "bin"))

    def package_id(self):
        # Verilator is a executable-only package, so the compiler version does not matter
        del self.info.settings.compiler.version

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        verilator_bin = "verilator_bin_dbg" if self.settings.build_type == "Debug" else "verilator_bin"
        self.output.info("Setting VERILATOR_BIN environment variable to {}".format(verilator_bin))
        self.env_info.VERILATOR_BIN = verilator_bin

        verilator_root = os.path.join(self.package_folder)
        self.output.info("Setting VERILATOR_ROOT environment variable to {}".format(verilator_root))
        self.env_info.VERILATOR_ROOT = verilator_root

        self.cpp_info.builddirs.append(os.path.join("bin", "share", "verilator"))
        self.cpp_info.build_modules.append(os.path.join("bin", "share", "verilator", "verilator-tools.cmake"))
