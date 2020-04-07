from conans import ConanFile, tools
import os
import shutil
import sys


class SConsConan(ConanFile):
    name = "scons"
    description = "SCons is an Open Source software construction tool—that is, a next-generation build tool"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://scons.org"
    topics = ("conan", "scons", "build", "configuration", "development")
    settings = "os"  # Added to let the CI test this package on all os'es

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("scons-{}".format(self.version), self._source_subfolder)

    def build(self):
        with tools.chdir(self._source_subfolder):
            self.run("{} setup.py build -j{}".format(sys.executable, tools.cpu_count()))

    def package(self):
        self.copy("LICENSE*", src=self._source_subfolder, dst="licenses")

        # Mislead CI and create an empty header in the include directory
        include_dir = os.path.join(self.package_folder, "include")
        os.mkdir(include_dir)
        tools.save(os.path.join(include_dir, "__nop.h"), "")

        with tools.chdir(self._source_subfolder):
            self.run("{} setup.py install --no-compile --prefix={}".format(sys.executable, self.package_folder))

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

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment var: {}".format(bindir))
        self.env_info.PATH.append(bindir)

        scons_pythonpath = os.path.join(self.package_folder, "lib", "site-packages", "scons")
        self.output.info("Appending PYTHONPATH environment var: {}".format(scons_pythonpath))
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "site-packages", "scons"))
