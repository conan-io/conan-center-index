from conans import ConanFile, AutoToolsBuildEnvironment, tools
from contextlib import contextmanager
import glob
import os
import shutil


class VerilatorConan(ConanFile):
    name = "verilator"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.veripool.org/wiki/verilator"
    description = "Verilator compiles synthesizable Verilog and Synthesis assertions into single- or multithreaded C++ or SystemC code"
    topics = ("conan", "verilog", "HDL", "EDA", "simulator", "hardware", "fpga")
    exports_sources = "patches/**"

    settings = "os", "arch", "compiler", "build_type"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            if self.settings.compiler == "Visual Studio":
                self.build_requires("msys2/20190524")
                self.build_requires("automake/1.16.2")
            self.build_requires("winflexbison/2.5.22")
            self.build_requires("strawberryperl/5.30.0.1")
        else:
            self.build_requires("flex/2.6.4")
            self.build_requires("bison/3.5.3")

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("strawberryperl/5.30.0.1")
        if self.settings.compiler == "Visual Studio":
            self.requires("dirent/1.23.2", private=True)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("verilator-{}".format(self.version), self._source_subfolder)

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
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        try:
            os.unlink(os.path.join(self._source_subfolder, "src", "config_build.h"))
        except FileNotFoundError:
            pass

        if self.settings.compiler == "Visual Studio":
            tools.replace_in_file(os.path.join(self._source_subfolder, "src", "Makefile_obj.in"),
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

        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "man"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "verilator", "examples"))

        os.unlink(os.path.join(self.package_folder, "bin", "share", "verilator", "verilator-config-version.cmake"))
        os.rename(os.path.join(self.package_folder, "bin", "share", "verilator", "verilator-config.cmake"),
                  os.path.join(self.package_folder, "bin", "share", "verilator", "verilator-tools.cmake"))

        if self.settings.build_type == "Debug":
            tools.replace_in_file(os.path.join(self.package_folder, "bin", "share", "verilator", "verilator-tools.cmake"),
                                  "verilator_bin", "verilator_bin_dbg")

        shutil.move(os.path.join(self.package_folder, "bin", "share", "verilator", "include"),
                    os.path.join(self.package_folder))

        for fn in glob.glob(os.path.join(self.package_folder, "bin", "share", "verilator", "bin", "*")):
            print(fn, "->", "..")
            os.rename(fn, os.path.join(self.package_folder, "bin", os.path.basename(fn)))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "verilator", "bin"))

    def package_id(self):
        # Verilator is a executable-only package, so the compiler version does not matter
        del self.info.settings.compiler.version

    def package_info(self):
        verilator_include_root = os.path.join(self.package_folder, "share", "verilator", "include")

        self.cpp_info.includedirs = [verilator_include_root]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        verilator_bin = "verilator_bin_dbg" if self.settings.build_type == "Debug" else "verilator_bin"
        self.output.info("Setting VERILATOR_BIN environment variable to {}".format(verilator_bin))
        self.env_info.VERILATOR_BIN = verilator_bin

        verilator_root = os.path.join(self.package_folder)
        self.output.info("Setting VERILATOR_ROOT environment variable to {}".format(verilator_root))
        self.env_info.VERILATOR_ROOT = verilator_root

        self.cpp_info.builddirs = [os.path.join("bin", "share", "verilator")]
        self.cpp_info.build_modules = [os.path.join("bin", "share", "verilator", "verilator-tools.cmake")]
