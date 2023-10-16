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
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def generate(self):
        pcre2_cpp_info = self.dependencies["pcre2"].cpp_info.aggregated_components()
        save(self, os.path.join(self.build_folder, "bindir"), pcre2_cpp_info.bindir)
        save(self, os.path.join(self.build_folder, "libdir"), pcre2_cpp_info.libdir)
        save(self, os.path.join(self.build_folder, "libs"), " ".join(pcre2_cpp_info.libs))

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            bin_path = os.path.join(self.cpp.build.bindir, "test_package")
            self.run(bin_path, env="conanrun")

            if Version(self.tested_reference_str.split("/")[1]) >= "10.36":
                bindir = load(self, os.path.join(self.build_folder, "bindir"))
                libdir = load(self, os.path.join(self.build_folder, "libdir")).replace("\\", "/")
                libs = load(self, os.path.join(self.build_folder, "libs")).split(" ")
                output = StringIO()
                self.run(f"bash {bindir}/pcre2-config --libs8", output)
                conf = next(l for l in output.getvalue().splitlines() if l.lower().startswith("-l")).strip().split(" ")
                assert f"-L{libdir}" in conf, f"Expected '-L{libdir}' not set by pcre2-config: {conf}"
                for param in conf:
                    if param.startswith("-l"):
                        assert param[2:] in libs, f"Invalid library target '{param[2:]}' output by pcre2-config. Not found in {libs}."
