from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.definitions["PYTHON_EXECUTABLE"] = tools.get_env("PYTHON")
        cmake.definitions["Python_ADDITIONAL_VERSIONS"] = ".".join(self.deps_cpp_info["cpython"].version.split(".")[:2])
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self.settings, skip_x64_x86=True):
            self.run("{} -c \"print('hello world')\"".format(tools.get_env("PYTHON")), run_environment=True)
            if self.options["cpython"].with_bz2:
                self.run("{} {}".format(tools.get_env("PYTHON"), os.path.join(self.source_folder, "test_bz2.py")), run_environment=True)
            if self.options["cpython"].with_lzma:
                self.run("{} {}".format(tools.get_env("PYTHON"), os.path.join(self.source_folder, "test_lzma.py")), run_environment=True)
            self.run("{} {}".format(tools.get_env("PYTHON"), os.path.join(self.source_folder, "test_expat.py")), run_environment=True)

            with tools.environment_append({"PYTHONPATH": [os.path.join(self.build_folder, "lib")]}):
                self.run("{} {}".format(tools.get_env("PYTHON"), os.path.join(self.source_folder, "test_spam.py")), run_environment=True)

            self.run(os.path.join("bin", "test_package"), run_environment=True)
