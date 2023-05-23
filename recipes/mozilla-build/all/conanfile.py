from conan import ConanFile
from conan.tools.files import download
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.52.0"

class MozillaBuildConan(ConanFile):
    name = "mozilla-build"
    homepage = "https://wiki.mozilla.org/MozillaBuild"
    description = "Mozilla build requirements on Windows"
    topics = ("mozilla", "build")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "arch", "build_type", "compiler", "os"
    license = "MPL-2.0"

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("Only Windows supported")

    def build_requirements(self):
        self.build_requires("7zip/19.00")

    def build(self):
        filename = "mozilla-build.exe"
        download(self, **self.conan_data["sources"][self.version][0], filename=filename)
        download(self, **self.conan_data["sources"][self.version][1], filename="LICENSE")
        self.run(f"7z x {filename}", run_environment=True)


    def package(self):
        self.copy("LICENSE", dst="licenses")
        self.copy("nsinstall.exe", src="bin", dst="bin")

    def package_id(self):
        del self.info.settings.build_type
        del self.info.settings.compiler

    def package_info(self):
        self.cpp_info.includedirs = []
        binpath = os.path.join(self.package_folder, "bin")
        self.output.info(f"Adding to PATH: {binpath}")
        self.env_info.PATH.append(binpath)
