from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.files import save, load
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.scm import Version
import os
from io import StringIO


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeToolchain", "CMakeDeps", "VirtualRunEnv"
    test_type = "explicit"

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

    def generate(self):
        # Workaround for Conan v1: store dependency info for later use in test()
        pcre2_cpp_info = self.dependencies["pcre2"].cpp_info.aggregated_components()
        save(self, os.path.join(self.build_folder, "bindir"), pcre2_cpp_info.bindir)
        save(self, os.path.join(self.build_folder, "libs"), " ".join(pcre2_cpp_info.libs))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")

            # Check that pcre2-config outputs correct link flags
            if Version(self.tested_reference_str.split("/")[1]) >= "10.38":
                bindir = load(self, os.path.join(self.build_folder, "bindir"))
                libs = load(self, os.path.join(self.build_folder, "libs")).split(" ")
                output = StringIO()
                self.run(f"bash {bindir}/pcre2-config --libs8", output)
                ldflags_str = next(l for l in output.getvalue().splitlines() if l.lower().startswith("-l")).strip()
                ldflags = ldflags_str.split()
                for flag in ldflags:
                    if flag.startswith("-l"):
                        assert flag[2:] in libs, f"Invalid library target '{flag[2:]}' output by pcre2-config. Not found in {libs}."
