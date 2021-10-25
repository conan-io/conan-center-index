from conans import ConanFile, tools
from conans.errors import ConanException, ConanInvalidConfiguration
import io
import os
import shutil
import sys


class SConsConan(ConanFile):
    name = "scons"
    description = "SCons is an Open Source software construction tool-that is, a next-generation build tool"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://scons.org"
    topics = ("scons", "build", "configuration", "development")
    settings = "os"  # Added to let the CI test this package on all os'es

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        # Detect availability of a python interpreter
        # FIXME: add a python build requirement
        if not tools.which("python"):
            raise ConanInvalidConfiguration("This recipe requires a python interpreter.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    @property
    def _python_executable(self):
        return "python"
    
    @property
    def _scons_pythonpath(self):
        return os.path.join(self.package_folder, "lib", "site-packages", "scons")

    def build(self):
        with tools.chdir(self._source_subfolder):
            output = io.StringIO()
            self.run("{} setup.py --requires".format(self._python_executable), output=output)
            # Workaround for log.print_run_commands = True/False
            # This requires log.run_to_output = True
            if not (output.getvalue().strip().splitlines() or ["-"])[-1].startswith("-"):
                raise ConanException("scons has a requirement")
            self.run("{} setup.py build".format(self._python_executable))

    def package(self):
        self.copy("LICENSE*", src=self._source_subfolder, dst="licenses")

        # Mislead CI and create an empty header in the include directory
        include_dir = os.path.join(self.package_folder, "include")
        os.mkdir(include_dir)
        tools.save(os.path.join(include_dir, "__nop.h"), "")

        with tools.chdir(self._source_subfolder):
            with tools.environment_append({"PYTHONPATH": [self._scons_pythonpath]}):
                self.run("{} setup.py install --no-compile --prefix={}".format(self._python_executable, self.package_folder))

        tools.rmdir(os.path.join(self.package_folder, "man"))

        if tools.os_info.is_windows:
            # On Windows, scons installs the scripts in the folders `Scripts" and `Lib".
            # Move these to the directories "bin" and "lib".
            shutil.move(os.path.join(self.package_folder, "Scripts"),
                        os.path.join(self.package_folder, "bin"))
            # Windows has case-insensitive paths, so do Lib -> lib2 -> lib
            shutil.move(os.path.join(self.package_folder, "Lib"),
                        os.path.join(self.package_folder, "lib2"))
            shutil.move(os.path.join(self.package_folder, "lib2"),
                        os.path.join(self.package_folder, "lib"))

        # Check for compiled python sources
        for root, _, files in os.walk(self.package_folder):
            for file in files:
                for ext in (".pyc", ".pyo", "pyd"):
                    if ext in file:
                        fullpath = os.path.join(root, file)
                        os.unlink(fullpath)
                        self.output.warn("Found compiled python code: {}".format(fullpath))
                if file.endswith(".egg-info"):
                    os.unlink(os.path.join(root, file))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment var: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        self.output.info("Appending PYTHONPATH environment var: {}".format(self._scons_pythonpath))
        self.env_info.PYTHONPATH.append(self._scons_pythonpath)
