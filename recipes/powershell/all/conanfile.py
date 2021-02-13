from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import glob
import os


class PowershellConan(ConanFile):
    name = "powershell"
    description = ("PowerShell Core is a cross-platform (Windows, Linux, "
                   "and macOS) automation and configuration tool/framework.")
    license = "MIT"
    topics = ("conan", "powershell", "command-line", "shell")
    homepage = "https://docs.microsoft.com/fr-fr/powershell/"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os_build", "arch_build"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        sources_url_per_os_arch = self.conan_data["sources"][self.version]["url"]
        the_os = str(self.settings.os_build)
        if the_os not in sources_url_per_os_arch:
            raise ConanInvalidConfiguration("powershell does not support {0}".format(the_os))
        arch = str(self.settings.arch_build)
        if arch not in sources_url_per_os_arch[the_os]:
            raise ConanInvalidConfiguration("powershell does not support {0} {1}".format(the_os, arch))

    def source(self):
        pass

    def build(self):
        the_os = str(self.settings.os_build)
        arch = str(self.settings.arch_build)
        url = self.conan_data["sources"][self.version]["url"][the_os][arch]
        sha256 = self.conan_data["sources"][self.version]["sha256"][the_os][arch]
        tools.get(url, sha256=sha256, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="bin", src=self._source_subfolder)
        self._fix_permissions()

    def _fix_permissions(self):

        def chmod_plus_x(name):
            os.chmod(name, os.stat(name).st_mode | 0o111)

        if self.settings.os_build != "Windows":
            chmod_plus_x(os.path.join(self.package_folder, "bin", "pwsh"))

    def package_info(self):
        bin_dir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_dir))
        self.env_info.PATH.append(bin_dir)
