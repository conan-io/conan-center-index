from conan import ConanFile


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"
    test_type = "explicit"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def test(self):
        make = self.conf.get("tools.gnu:make_program", check_type=str)
        self.run(f"{make} -C {self.source_folder} love")
