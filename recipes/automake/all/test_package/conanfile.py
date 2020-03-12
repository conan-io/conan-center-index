from conans import AutoToolsBuildEnvironment, ConanFile, tools
from contextlib import contextmanager
import os
import shutil


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "configure.ac", "Makefile.am", "test_package_1.c", "test_package.cpp"

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                with tools.environment_append({"CC": "cl -nologo", "CXX": "cl -nologo",}):
                    yield
        else:
            yield

    _default_cc = {
        "gcc": "gcc",
        "clang": "clang",
        "Visual Studio": "cl -nologo",
        "apple-clang": "clang",
    }

    @property
    def _system_cc(self):
        system_cc = os.environ.get("CC", None)
        if not system_cc:
            system_cc = self._default_cc.get(str(self.settings.compiler))
        return system_cc

    def _build_scripts(self):
        """Test compile script of automake"""
        compile_script = self.deps_user_info["automake"].compile
        ar_script = self.deps_user_info["automake"].ar_lib
        assert os.path.isfile(ar_script)
        assert os.path.isfile(compile_script)

        if self._system_cc:
            with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
                self.run("{} {} test_package_1.c -o script_test".format(tools.unix_path(compile_script), self._system_cc), win_bash=tools.os_info.is_windows)

    def _build_autotools(self):
        """Test autoreconf + configure + make"""
        self.run("{} --verbose --install".format(os.environ["AUTORECONF"]), win_bash=tools.os_info.is_windows)
        self.run("{} --help".format(os.path.join(self.build_folder, "configure").replace("\\", "/")), win_bash=tools.os_info.is_windows)
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools.configure()
            autotools.make()

    def build(self):
        for src in self.exports_sources:
            shutil.copy(os.path.join(self.source_folder, src), self.build_folder)

        self._build_scripts()
        self._build_autotools()

    def test(self):
        if self._system_cc:
            if not tools.cross_building(self.settings):
                self.run(os.path.join(".", "script_test"), run_environment=True)

        if not tools.cross_building(self.settings):
            self.run(os.path.join(".", "test_package"), run_environment=True)
