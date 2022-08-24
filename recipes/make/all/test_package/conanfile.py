from conans import ConanFile, AutoToolsBuildEnvironment, tools
import contextlib


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    @contextlib.contextmanager
    def _build_context(self):
        if hasattr(self, "settings_build"):
            # Environments are not inherited when cross building, so manually set the `CONANMAKE_PROGRAM' environment variable
            with tools.environment_append({"CONAN_MAKE_PROGRAM": self.deps_user_info["make"].make}):
                yield
        else:
            yield

    def test(self):
        if not tools.build.cross_building(self, self):
            with tools.files.chdir(self, self.source_folder):
                with self._build_context():
                    env_build = AutoToolsBuildEnvironment(self)
                    env_build.make(args=["love"])
