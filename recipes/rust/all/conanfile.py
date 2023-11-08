import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, download, unzip, rm, rmdir


class RustConan(ConanFile):
    name = "rust"
    description = "The Rust Programming Language"
    license = "MIT", "Apache-2.0"
    homepage = "https://www.rust-lang.org"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("rust", "language", "rust-language", "pre-built")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    @property
    def _os_name(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            return "Linux"
        return str(self.settings.os)

    @property
    def _rust_download_info(self):
        arch_name = str(self.settings.arch)
        return self.conan_data["sources"][self.version].get(self._os_name, {}).get(arch_name)

    def validate(self):
        if not self._rust_download_info:
            raise ConanInvalidConfiguration(f"Unsupported OS/arch combination: {self.settings.os}/{self.settings.arch}")

    def build(self):
        dl_info = self._rust_download_info
        file_name = dl_info["url"].rsplit("/", 1)[-1]
        extension = file_name.split(".", 1)[-1]
        download(self, **dl_info, filename=file_name)

        if extension == "msi":
            self.run(f"msiexec /a {file_name} /qn TARGETDIR={self.build_folder}/rust")
        elif extension == "pkg":
            self.run(f"xar -xf {file_name}")
        else:
            unzip(self, file_name, self.build_folder, strip_root=True)

        os.remove(file_name)


    def package(self):
        copy(self, "LICENSE-APACHE", self.build_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE-MIT", self.build_folder, os.path.join(self.package_folder, "licenses"))
        # Merge all Rust components into the package folder
        for dir in self.build_path.iterdir():
            if dir.is_dir() and "docs" not in dir.name:
                self.output.info(f"Copying {dir.name} contents to {self.package_folder}")
                copy(self, "*", dir, self.package_folder)
        rm(self, "manifest.in", self.package_folder)
        rmdir(self, os.path.join(self.package_folder, "libexec"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "etc"))

    def package_info(self):
        self.cpp_info.includedirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "m", "pthread", "rt"]
