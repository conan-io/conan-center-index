from conans import ConanFile, AutoToolsBuildEnvironment, tools


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def test(self):
        if not tools.cross_building(self):
            with tools.chdir(self.source_folder), tools.remove_from_path("make"):
                env_build = AutoToolsBuildEnvironment(self)
                env_build.make(args=["love"])
