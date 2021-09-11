from conans import AutoToolsBuildEnvironment, ConanFile, tools
import contextlib
import functools
import os
import shutil

required_conan_version = ">=1.33.0"


class VerilatorConan(ConanFile):
    name = "verilator"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.veripool.org/wiki/verilator"
    description = "Verilator compiles synthesizable Verilog and Synthesis assertions into single- or multithreaded C++ or SystemC code"
    topics = ("verilog", "HDL", "EDA", "simulator", "hardware", "fpga")
    settings = "os", "arch", "compiler", "build_type"

    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        self.build_requires("automake/1.16.4")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            if self.settings.compiler == "Visual Studio":
                self.build_requires("msys2/cci.latest")
            self.build_requires("winflexbison/2.5.24")
            self.build_requires("strawberryperl/5.30.0.1")
        else:
            self.build_requires("flex/2.6.4")
            self.build_requires("bison/3.7.6")

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("strawberryperl/5.30.0.1")
        if self.settings.compiler == "Visual Studio":
            self.requires("dirent/1.23.2", private=True)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            build_env = {
                "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                "AR": "{} lib".format(tools.unix_path(self.deps_user_info["automake"].ar_lib)),
            }
            with tools.vcvars(self):
                with tools.environment_append(build_env):
                    yield
        else:
            yield

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.libs = []
        autotools.library_paths = []
        if self.settings.get_safe("compiler.libcxx") == "libc++":
            autotools.libs.append("c++")
        if self.settings.compiler == "Visual Studio":
            autotools.cxx_flags.append("-EHsc")
            autotools.defines.extend(["NOMINMAX", "YY_NO_UNISTD_H"])
            autotools.flags.extend(["-FS", "-std:c++14", "-Zc:__cplusplus"])
        conf_args = [
            "--datarootdir={}/bin/share".format(tools.unix_path(self.package_folder)),
        ]
        yacc = tools.get_env("YACC")
        if yacc:
            if yacc.endswith(" -y"):
                yacc = yacc[:-3]
        with tools.environment_append({"YACC": yacc}):
            autotools.configure(args=conf_args, configure_dir=os.path.join(self.build_folder, self._source_subfolder))
        return autotools

    @property
    def _make_args(self):
        args = [
            "CFG_WITH_DEFENV=false",
            "SRC_TARGET={}".format("dbg" if self.settings.build_type == "Debug" else "opt"),
            "DEBUG={}".format("1" if self.settings.build_type == "Debug" else "0"),
        ]
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
        with tools.chdir(self._source_subfolder):
            self.run(f"{tools.get_env('AUTOCONF')}", run_environment=True, win_bash=tools.os_info.is_windows)
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
        tools.rename(os.path.join(self.package_folder, "bin", "share", "verilator", "verilator-config.cmake"),
                     os.path.join(self.package_folder, "bin", "share", "verilator", "verilator-tools.cmake"))

        if self.settings.build_type == "Debug":
            tools.replace_in_file(os.path.join(self.package_folder, "bin", "share", "verilator", "verilator-tools.cmake"),
                                  "verilator_bin", "verilator_bin_dbg")

        shutil.move(os.path.join(self.package_folder, "bin", "share", "verilator", "include"),
                    os.path.join(self.package_folder))

        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin", "share", "verilator", "bin"), "*")
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
