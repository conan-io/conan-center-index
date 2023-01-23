from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import cross_building, can_run
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv, Environment
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, unix_path

import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    test_type = "explicit"
    short_paths = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", default=False, check_type=str):
                self.tool_requires("msys2/cci.latest")

    def layout(self):
        basic_layout(self)

    @property
    def package_folder(self):
        return os.path.join(self.build_folder, "autotools")

    def _generate_autotools(self):
        env = VirtualBuildEnv(self)
        env.generate()

        if not cross_building(self):
            env = VirtualRunEnv(self)
            env.generate(scope="build")

            run_env = VirtualRunEnv(self)
            run_env.generate()

        test_env = Environment()
        runtime_lib_path = unix_path(self, os.path.join(self.package_folder, "lib"))
        test_env.append_path("LD_LIBRARY_PATH", runtime_lib_path)
        test_env.append_path("DYLD_LIBRARY_PATH", runtime_lib_path)
        test_env.vars(self, scope="run").save_script("autotools_test")

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--enable-shared",
            "--enable-static"
        ])
        tc.generate()

        if is_msvc(self):
            env = Environment()
            compile_wrapper = unix_path(self, self._user_info_build["automake"].compile)
            ar_wrapper = unix_path(self, self._user_info_build["automake"].ar_lib)
            env.define("CC", f"{compile_wrapper} cl -nologo")
            env.define("CXX", f"{compile_wrapper} cl -nologo")
            env.define("LD", "link -nologo")
            env.define("AR", f"{ar_wrapper} \"lib -nologo\"")
            env.define("NM", "dumpbin -symbols")
            env.define("OBJDUMP", ":")
            env.define("RANLIB", ":")
            env.define("STRIP", ":")
            env.vars(self).save_script("conanbuild_msvc")

    def _generate_cmake(self):
        CMakeDeps(self).generate()
        CMakeToolchain(self).generate()

    def generate(self):
        self._generate_cmake()
        self._generate_autotools()

    def _build_ltdl(self):
        """ Build library using ltdl library """
        cmake = CMake(self)
        cmake.configure(build_script_folder="ltdl")
        cmake.build()

    def _test_ltdl(self):
        """ Test library using ltdl library"""
        lib_suffix = {
            "Linux": "so",
            "FreeBSD": "so",
            "Macos": "dylib",
            "Windows": "dll",
        }[str(self.settings.os)]

        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            lib_path = os.path.join(self.cpp.build.bindirs[0], f"liba.{lib_suffix}")
            self.run(f"{bin_path} {lib_path}", env="conanrun")

    def _build_autotools(self):
        """ Test autotools integration """
        autotools = Autotools(self)
        autotools.autoreconf(["--install", "autotools"])
        autotools.configure(build_script_folder="autotools")
        autotools.make()
        autotools.install(args=[f"DESTDIR={unix_path(self, self.package_folder)}"])
        fix_apple_shared_install_name(self)

    def _test_autotools(self):
        assert os.path.isdir(os.path.join(self.package_folder, "bin"))
        assert os.path.isfile(os.path.join(self.package_folder, "include", "lib.h"))
        assert os.path.isdir(os.path.join(self.package_folder, "lib"))

        if can_run(self):
            self.run(os.path.join(self.package_folder, "bin", "test_package"), env="conanrun")

    def build(self):
        self._build_ltdl()
        self._build_autotools()

    def test(self):
        self._test_ltdl()
        self._test_autotools()
