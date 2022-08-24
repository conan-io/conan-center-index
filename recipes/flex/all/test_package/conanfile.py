from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conans.errors import ConanException
import os


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def build_requirements(self):
        self.build_requires(self.tested_reference_str)

    def build(self):
        if not hasattr(self, "settings_build"):
            # Only test location of flex executable when not cross building
            flex_bin = tools.which("flex")
            if not flex_bin.startswith(self.deps_cpp_info["flex"].rootpath):
                raise ConanException("Wrong flex executable captured")

        if not tools.cross_building(self, skip_x64_x86=True) or hasattr(self, "settings_build"):
            self.run("flex --version", run_environment=not hasattr(self, "settings_build"))

            print(os.environ["PATH"])
            cmake = CMake(self)
            cmake.definitions["FLEX_ROOT"] = self.deps_cpp_info["flex"].rootpath
            cmake.configure()
            cmake.build()

    def test(self):
        if not tools.cross_building(self, skip_x64_x86=True):
            bin_path = os.path.join("bin", "test_package")
            src = os.path.join(self.source_folder, "basic_nr.txt")
            self.run("{} {}".format(bin_path, src), run_environment=True)

            test_yywrap = os.path.join("bin", "test_yywrap")
            self.run(test_yywrap, run_environment=True)
