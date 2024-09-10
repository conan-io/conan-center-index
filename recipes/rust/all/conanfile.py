import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, rm, rmdir, get


class RustConan(ConanFile):
    name = "rust"
    description = "The Rust Programming Language"
    license = "MIT", "Apache-2.0"
    homepage = "https://www.rust-lang.org"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("rust", "language", "rust-language", "pre-built")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    upload_policy = "skip"
    build_policy = "missing"

    def layout(self):
        pass

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    @property
    def _rust_download_info(self):
        os_name = str(self.settings.os)
        arch_name = str(self.settings.arch)
        version_info = self.conan_data["sources"][self.version]
        if os_name == "Windows":
            compiler_name = "gcc" if self.settings.compiler == "gcc" else "msvc"
            return version_info[os_name][compiler_name].get(arch_name)
        else:
            return version_info.get(os_name, {}).get(arch_name)

    def validate(self):
        if not self._rust_download_info:
            raise ConanInvalidConfiguration(f"Unsupported OS/arch combination: {self.settings.os}/{self.settings.arch}")

    def build(self):
        get(self, **self._rust_download_info, strip_root=True)

    def package(self):
        copy(self, "LICENSE-APACHE", self.build_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSE-MIT", self.build_folder, os.path.join(self.package_folder, "licenses"))
        # Merge all Rust components into the package folder
        for path in self.build_path.iterdir():
            if path.is_dir() and "docs" not in path.name:
                self.output.info(f"Copying {path.name} contents to {self.package_folder}")
                copy(self, "*", path, self.package_folder)
        rm(self, "manifest.in", self.package_folder)
        rm(self, "*.pdb", self.package_folder, recursive=True)
        rmdir(self, os.path.join(self.package_folder, "libexec"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "etc"))

    def package_info(self):
        self.cpp_info.includedirs = []

        # https://doc.rust-lang.org/cargo/reference/environment-variables.html
        self.buildenv_info.define_path("CARGO", os.path.join(self.package_folder, "bin", "cargo"))
        self.buildenv_info.define_path("RUSTC", os.path.join(self.package_folder, "bin", "rustc"))
        self.buildenv_info.define_path("RUSTDOC", os.path.join(self.package_folder, "bin", "rustdoc"))
        self.buildenv_info.define_path("RUSTFMT", os.path.join(self.package_folder, "bin", "rustfmt"))
