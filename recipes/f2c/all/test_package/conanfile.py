import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain
from conan.tools.env import Environment
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime, VCVars, unix_path


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "VirtualBuildEnv", "VirtualRunEnv"
    test_type = "explicit"
    win_bash = True

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        if self._settings_build.os == "Windows":
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")
            if is_msvc(self):
                self.tool_requires("automake/1.16.5")

    def generate(self):
        if is_msvc(self):
            VCVars(self).generate()

            env = Environment()
            automake_conf = self.dependencies.build["automake"].conf_info
            compile_wrapper = unix_path(self, automake_conf.get("user.automake:compile-wrapper", check_type=str))
            crt = "-MT" if is_msvc_static_runtime(self) else "-MD"
            env.define("CC", f"{compile_wrapper} cl -nologo {crt}")
            env.define("LD", "link lib")
            env.vars(self).save_script("conanbuild_msvc")

            tc = CMakeToolchain(self, generator="MSYS Makefiles")
            fc = os.path.join(self.dependencies["f2c"].package_folder, "bin", "fc")
            tc.cache_variables["CMAKE_Fortran_COMPILER"] = fc.replace("\\", "/")
            tc.generate()
        else:
            tc = CMakeToolchain(self)
            tc.generate()

    def build(self):
        src_file = unix_path(self, os.path.join(self.source_folder, "test_package.f"))
        self.run(f"f2c < '{src_file}'")

        self.run("$FC --version")
        self.run(f"$FC {src_file} -o test_package_direct")

        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = unix_path(self, os.path.join(self.build_folder, "test_package_direct"))
            self.run(bin_path, env="conanrun")
            bin_path = unix_path(self, os.path.join(self.build_folder, "test_package"))
            self.run(bin_path, env="conanrun")
