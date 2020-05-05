from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class GoogleguetzliConan(ConanFile):
    name = "google-guetzli"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://opensource.google/projects/guetzli"
    description = "Perceptual JPEG encoder"
    topics = "jpeg","compression"
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"
    requires = ["libpng/1.6.37"]

    _source_subfolder = "source_subfolder"

    @property
    def on_windows(self):
        return self.settings.os == "Windows"

    def configure(self):
        if self.settings.os not in ["Linux","Windows"]:
            raise ConanInvalidConfiguration("conan recipe for  google-guetzli v{0} is not \
                available in {1}.".format(self.version, self.settings.os))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "guetzli-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        if self.on_windows:
            from conans import MSBuild
            msbuild = MSBuild(self)
            with tools.chdir(self._source_subfolder):
                msbuild.build("guetzli.sln")
        else:
            with tools.chdir(self._source_subfolder):
                print("cwd = {}".format(os.getcwd()))
                with tools.environment_append({"PKG_CONFIG_PATH": self.build_folder}):
                    self.run("make")
            
    def package(self):
        if self.on_windows:
            self.copy("{}/bin/{}/Release/guetzli.exe".format(self._source_subfolder, self.settings.arch),
                      dst="bin", keep_path=False)
        else:
            self.copy("{}/bin/Release/guetzli".format(self._source_subfolder), dst="bin", keep_path=False)
        self.copy("{}/LICENSE".format(self._source_subfolder), dst="licenses")

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)

