from conans import ConanFile, CMake, tools
import contextlib
import functools
import os
import re
import textwrap


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake", "cmake_find_package"

    @property
    def _with_systemc_example(self):
        # systemc is not available on Macos
        return self.settings.os != "Macos" and self._detect_cppstd() >= 2011

    def requirements(self):
        if self._with_systemc_example:
            self.requires("systemc/2.3.3")

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                with tools.environment_append({"CPP": "cl -E"}):
                    yield
        else:
            cpp = None
            if tools.get_env("CXX"):
                cpp = "{} -E".format(tools.get_env("CXX"))
            if not cpp:
                cpp = "g++ -E"
            with tools.environment_append({"CPP": cpp}):
                yield

    @functools.lru_cache(1)
    def _detect_cppstd(self):
        if self.settings.compiler.cppstd:
            return int({
                "98": 1998,
            }.get(str(self.settings.compiler.cppstd), int(f"20{self.settings.compiler.cppstd}")))
        tools.save("_tmp.cpp", textwrap.dedent("""\
            int cplusplus = __cplusplus;
        """))
        with self._build_context():
            self.run(f"{tools.get_env('CPP')} _tmp.cpp >output.txt", run_environment=True)
        cplusplus_match = next(re.finditer("cplusplus = ([0-9]+)[L]?;", tools.load("output.txt")))
        cplusplus = int(cplusplus_match.group(1))
        self.output.info(f"C++ compiler reports __cplusplus={cplusplus}")
        cppstds = (
            (199711, 1998),
            (201103, 2011),
            (201402, 2014),
            (201703, 2017),
            (202002, 2020),
        )
        try:
            cppstd = next(std for macro, std in cppstds if macro >= cplusplus)
        except StopIteration:
            self.output.warn("Could not detect the c++ standard. Assuming cppstd=23.")
            cppstd = 23
        self.output.info(f"Detected cppstd={cppstd}")
        return cppstd

    def build(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            with tools.run_environment(self):
                with tools.environment_append({"VERILATOR_ROOT": self.deps_user_info["verilator"].verilator_root}):
                    cmake = CMake(self)
                    cmake.definitions["BUILD_SYSTEMC"] = self._with_systemc_example
                    cmake.configure()
                    cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            with tools.run_environment(self):
                self.run("perl {} --version".format(os.path.join(self.deps_cpp_info["verilator"].rootpath, "bin", "verilator")), run_environment=True)
            self.run(os.path.join("bin", "blinky"), run_environment=True)
            if self._with_systemc_example:
                self.run(os.path.join("bin", "blinky_sc"), run_environment=True)
