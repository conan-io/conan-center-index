from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os


class MozillaBuildConan(ConanFile):
    name = "mozilla-build"
    homepage = "https://wiki.mozilla.org/MozillaBuild"
    description = "Mozilla build requirements on Windows"
    topics = ("conan", "mozilla", "build")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os_build", "arch_build"
    license = "MPL-2.0"

    def configure(self):
        if self.settings.os_build != "Windows":
            raise ConanInvalidConfiguration("Only Windows supported")

    def build_requirements(self):
        self.build_requires("7zip/19.00")

    def build(self):
        url = self.conan_data["sources"][self.version]["url"]
        tools.download(url, "mozilla-build.exe")
        tools.check_sha256("mozilla-build.exe", self.conan_data["sources"][self.version]["sha256"])
        self.run("7z x mozilla-build.exe")
        os.unlink("mozilla-build.exe")
        tools.download("https://www.mozilla.org/media/MPL/2.0/index.815ca599c9df.txt", "LICENSE")

    def package(self):
        self.copy("LICENSE", dst="licenses")
        self.copy("nsinstall.exe", src="bin", dst="bin")

    def package_info(self):
        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Adding to PATH: {}".format(binpath))
        self.env_info.PATH.append(binpath)
