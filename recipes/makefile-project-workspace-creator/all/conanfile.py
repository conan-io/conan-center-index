import os
from conan import ConanFile, tools


class MPCGeneratorConan(ConanFile):
    name = "makefile-project-workspace-creator"
    description = "The Makefile, Project and Workspace Creator"
    license = "BSD-3-Clause"
    homepage = "https://objectcomputing.com/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "makefile-project-workspace-creator", "objectcomputing", "installer")
    settings = "os"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("strawberryperl/5.30.0.1")

    def build(self):
        pass

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("MPC-MPC_" + self.version.replace(".", "_"), self._source_subfolder)

    def package(self):
        self.copy(pattern="*", src=self._source_subfolder, dst="bin")
        self.copy(pattern="LICENSE", src=os.path.join(self._source_subfolder, "docs"), dst="licenses")

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info('Appending PATH environment variable: %s' % bin_path)
        self.env_info.PATH.append(bin_path)
        self.env_info.MPC_ROOT = bin_path
