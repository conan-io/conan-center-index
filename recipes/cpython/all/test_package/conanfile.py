from io import StringIO
from pathlib import Path

from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeDeps, CMakeToolchain
from conan.tools.scm import Version
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv, Environment
from conan.tools.microsoft import is_msvc
from conan.errors import ConanException
from conan.tools.files import chdir


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    @property
    def _supports_modules(self):
        return not is_msvc(self) or self.options["cpython"].shared

    def _cpython_option(self, name):
        try:
            return getattr(self.options["cpython"], name, False)
        except ConanException:
            return False

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        # py_version = Version(self.deps_cpp_info["cpython"].version)
        py_version = Version("3.10.4")
        cmake_layout(self, src_folder=f"py{py_version.major}")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["BUILD_MODULE"] = not is_msvc(self) or self.options["cpython"].shared
        tc.generate()

        vb = VirtualBuildEnv(self)
        vb.generate()

        # env = Environment()
        # env.define("DISTUTILS_USE_SDK", "1")
        # env.define("MSSdk", "1")
        # env_vars = env.vars(self, scope = "conanbuild")
        # env_vars.save_script("setupenv")

        if can_run(self):
            env = Environment()
            env.define("DISTUTILS_USE_SDK", "1")
            env.define("MSSdk", "1")

            if self._cpython_option("with_curses"):
                env.define("TERM", "ansi")
            if is_apple_os(self) and not self.options["cpython"].shared:
                env.append_path("PYTHONPATH", self.build_folder)
            env_vars = env.vars(self, scope="conanrun")
            env_vars.save_script("modenv")

            vr = VirtualRunEnv(self)
            vr.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        if not is_msvc(self) or self.options["cpython"].shared:
            setup_args = [
                self.source_path.joinpath("setup.py"),
                "build",
                "--build-base", self.build_folder,
                "--build-platlib", self.build_path,  #.joinpath("lib_setuptools"),
            ]
            if self.settings.build_type == "Debug":
                setup_args.append("--debug")
            self.run("python {}".format(" ".join("\"{}\"".format(a) for a in setup_args)), env="conanbuild", run_environment=True, cwd=self.source_folder)

    def _test_module(self, module, should_work):
        exception = None
        try:
            self.run(f"python {self.source_path.parent.joinpath('test_package.py')} -b {self.build_folder} -t {module} ", run_environment=True, env="conanrun")
            works = True
        except ConanException as e:
            works = False
            exception = e
        if should_work == works:
            self.output.info("Result of test was expected.")
        else:
            if works:
                raise ConanException(f"Module '{module}' works, but should not have worked")
            else:
                self.output.warn(f"Module '{module}' does not work, but should have worked")
                raise exception

    def test(self):
        if can_run(self):
            buffer = StringIO()
            self.run("python -c \"import sys; from pathlib import Path; print(Path(sys.executable).parent)\"", output=buffer, env="conanrun")
            self.output.info(buffer.getvalue())
            which_detected = buffer.getvalue().splitlines()[-1].strip()
            if which_detected not in str(Path(self.deps_user_info["cpython"].python).parent):
                raise ConanException(f"python reported wrong interpreter. Expected {self.deps_user_info['cpython'].python}. Got {which_detected}.")

            self.run("python -c \"import sys; print('.'.join(str(s) for s in sys.version_info[:3]))\"", output=buffer, env="conanrun")
            self.output.info(buffer.getvalue())
            version_detected = buffer.getvalue().splitlines()[-1].strip()
            if self.deps_cpp_info["cpython"].version != version_detected:
                raise ConanException(f"python reported wrong version. Expected {self._py_version}. Got {version_detected}.")

            if self._supports_modules:
                self._test_module("gdbm", self._cpython_option("with_gdbm"))
                self._test_module("bz2", self._cpython_option("with_bz2"))
                self._test_module("bsddb", self._cpython_option("with_bsddb"))
                self._test_module("lzma", self._cpython_option("with_lzma"))
                self._test_module("tkinter", self._cpython_option("with_tkinter"))
                self._test_module("curses", self._cpython_option("with_curses"))
                self._test_module("expat", True)
                self._test_module("sqlite3", True)
                self._test_module("decimal", True)
                self._test_module("ctypes", True)

            if is_apple_os(self) and not self.options["cpython"].shared:
                self.output.info("Not testing the module, because these seem not to work on apple when cpython is built as a static library")
                # FIXME: find out why cpython on apple does not allow to use modules linked against a static python
            else:
                if self._supports_modules:
                    self.output.info("Testing module (spam) using cmake built module")
                    self._test_module("spam", True)
                    self.output.info("Testing module (spam) using cmake built module python_add_library")
                    self._test_module("spam2", True)
                    self.output.info("Testing module (spam) using setup.py built module")
                    self._test_module("spam3", True)

            self.run(self.build_path.joinpath("test_package"), env = "conanrun")
