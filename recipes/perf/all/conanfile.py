from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.35.0"

class Perf(ConanFile):
    name = "perf"
    description = "Linux profiling with performance counters"
    topics = ("linux", "profiling")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://perf.wiki.kernel.org/index.php"
    license = "GPL-2.0 WITH Linux-syscall-note"
    settings = "os", "compiler", "build_type", "arch"

    _source_subfolder = "source_subfolder"


    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("perf is supported only on Linux")

    def system_requirements(self):
        installer = SystemPackageTool()
        for package in [ "flex", "bison" ]:
            installer.install(package)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(os.path.join(self.build_folder, self._source_subfolder, "tools", "perf")):
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

        self.copy("perf", src=os.path.join(self._source_subfolder, "tools", "perf"), dst="bin")

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: %s" % bin_path)
        self.env_info.PATH.append(bin_path)
