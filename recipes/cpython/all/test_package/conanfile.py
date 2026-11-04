import os
from io import StringIO

from conan import ConanFile, conan_version
from conan.errors import ConanException
from conan.tools.apple import is_apple_os
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.gnu import AutotoolsDeps
from conan.tools.microsoft import is_msvc, VCVars
from conan.tools.scm import Version

conan2 = conan_version.major >= 2

class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        # The main recipe does not require CMake, but we test with it.
        # The interesting problem that arises here is if you have CMake installed
        # with your global pip, then it will fail to run in this test package.
        # To avoid that, just add a requirement on CMake.
        self.tool_requires("cmake/[>=3.16 <4]")

    def layout(self):
        cmake_layout(self)

    @property
    def _python(self):
        if conan2:
            return self.dependencies["cpython"].conf_info.get("user.cpython:python", check_type=str)
        else:
            return self.deps_user_info["cpython"].python

    def _cpython_option(self, name):
        if conan2:
            return self.dependencies["cpython"].options.get_safe(name, False)
        else:
            try:
                return getattr(self.options["cpython"], name, False)
            except ConanException:
                return False

    @property
    def _py_version(self):
        if conan2:
            return Version(self.dependencies["cpython"].ref.version)
        else:
            return Version(self.deps_cpp_info["cpython"].version)

    @property
    def _test_setuptools(self):
        # TODO Should we still try to test this?
        # https://github.com/python/cpython/pull/101039
        return can_run(self) and self._supports_modules and self._py_version < "3.12"

    @property
    def _supports_modules(self):
        return not is_msvc(self) or self._cpython_option("shared")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_MODULE"] = self._supports_modules
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        try:
            # CMakeToolchain might generate VCVars, but we need it
            # unconditionally for the setuptools build.
            VCVars(self).generate()
        except ConanException:
            pass

        # The build also needs access to the run environment to run the python executable
        VirtualRunEnv(self).generate(scope="run")
        VirtualRunEnv(self).generate(scope="build")

        if self._test_setuptools:
            # Just for the distutils build
            AutotoolsDeps(self).generate(scope="build")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        if self._test_setuptools:
            os.environ["DISTUTILS_USE_SDK"] = "1"
            os.environ["MSSdk"] = "1"
            setup_args = [
                os.path.join(self.source_folder, "setup.py"),
                "build",
                "--build-base", self.build_folder,
                "--build-platlib", os.path.join(self.build_folder, "lib_setuptools"),
                # Bandaid fix: setuptools places temporary files in a subdirectory of the build folder where the
                # entirety of the absolute path up to this folder is appended (with seemingly no way to stop this),
                # essentially doubling the path length. This may run into Windows max path lengths, so we give ourselves
                # a little bit of wiggle room by making this directory name as short as possible. One of the directory
                # names goes from (for example) "temp.win-amd64-3.10-pydebug" to "t", saving us roughly 25 characters.
                "--build-temp", "t",
            ]
            if self.settings.build_type == "Debug":
                setup_args.append("--debug")
            args = " ".join(f'"{a}"' for a in setup_args)
            self.run(f"{self._python} {args}")

    def _test_module(self, module, should_work):
        try:
            self.run(f"{self._python} \"{self.source_folder}/test_package.py\" -b \"{self.build_folder}\" -t {module}", env="conanrun")
        except ConanException:
            if should_work:
                self.output.warning(f"Module '{module}' does not work, but should have worked")
                raise
            self.output.info("Module failed as expected")
            return
        if not should_work:
            raise ConanException(f"Module '{module}' works, but should not have worked")
        self.output.info("Module worked as expected")

    def test(self):
        if can_run(self):
            self.run(f"{self._python} --version", env="conanrun")

            self.run(f"{self._python} -c \"print('hello world')\"", env="conanrun")

            buffer = StringIO()
            self.run(f"{self._python} -c \"import sys; print('.'.join(str(s) for s in sys.version_info[:3]))\"", buffer, env="conanrun")
            self.output.info(buffer.getvalue())
            version_detected = buffer.getvalue().splitlines()[-1].strip()
            if self._py_version != version_detected:
                raise ConanException(
                    f"python reported wrong version. Expected {self._py_version}. Got {version_detected}."
                )

            if self._supports_modules:
                self._test_module("gdbm", self._cpython_option("with_gdbm"))
                self._test_module("bz2", self._cpython_option("with_bz2"))
                self._test_module("lzma", self._cpython_option("with_lzma"))
                self._test_module("tkinter", self._cpython_option("with_tkinter"))
                os.environ["TERM"] = "ansi"
                self._test_module("curses", self._cpython_option("with_curses"))
                self._test_module("expat", True)
                self._test_module("sqlite3", self._cpython_option("with_sqlite3"))
                self._test_module("decimal", True)
                self._test_module("ctypes", True)
                env = Environment()
                if self.settings.os != "Windows":
                    env.define_path("OPENSSL_CONF", os.path.join(os.sep, "dev", "null"))
                with env.vars(self).apply():
                    self._test_module("ssl", True)

            if is_apple_os(self) and not self._cpython_option("shared"):
                self.output.info(
                    "Not testing the module, because these seem not to work on apple when cpython is built as"
                    " a static library"
                )
                # FIXME: find out why cpython on apple does not allow to use modules linked against a static python
            else:
                if self._supports_modules:
                    os.environ["PYTHONPATH"] = os.path.join(self.build_folder, self.cpp.build.libdirs[0])
                    self.output.info("Testing module (spam) using cmake built module")
                    self._test_module("spam", True)

                    if self._test_setuptools:
                        os.environ["PYTHONPATH"] = os.path.join(self.build_folder, "lib_setuptools")
                        self.output.info("Testing module (spam) using setup.py built module")
                        self._test_module("spam", True)

                    del os.environ["PYTHONPATH"]

            # MSVC builds need PYTHONHOME set. Linux and Mac don't require it to be set if tested after building,
            # but if the package is relocated then it needs to be set.
            if conan2:
                os.environ["PYTHONHOME"] = self.dependencies["cpython"].conf_info.get("user.cpython:pythonhome", check_type=str)
            else:
                os.environ["PYTHONHOME"] = self.deps_user_info["cpython"].pythonhome
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
