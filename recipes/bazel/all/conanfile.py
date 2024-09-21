import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, rename, download

required_conan_version = ">=1.47.0"


class BazelConan(ConanFile):
    name = "bazel"
    package_type = "application"
    description = "Bazel is a fast, scalable, multi-language and extensible build system."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bazel.build/"
    topics = ("test", "build", "automation", "pre-built")
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    @property
    def _binary_info(self):
        os = str(self.settings.os)
        arch = str(self.settings.arch)
        return self.conan_data["sources"][self.version][os].get(arch)

    def validate(self):
        if self.settings.os not in ["Linux", "Macos", "Windows"]:
            raise ConanInvalidConfiguration("Only Linux, Windows and OSX are supported for this package.")
        if self._binary_info is None:
            raise ConanInvalidConfiguration(
                f"{self.settings.arch} architecture on {self.settings.os} is not supported for this package."
            )

    def source(self):
        pass

    @property
    def _bazel_filename(self):
        return self._binary_info["url"].rsplit("/")[-1]

    def build(self):
        download(self, **self._binary_info, filename=self._bazel_filename)
        download(self, **self.conan_data["sources"][self.version]["license"], filename="LICENSE")

    @property
    def _program_suffix(self):
        return ".exe" if self.settings.os == "Windows" else ""

    @staticmethod
    def _chmod_plus_x(name):
        os.chmod(name, os.stat(name).st_mode | 0o111)

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        copy(
            self,
            pattern=self._bazel_filename,
            dst=os.path.join(self.package_folder, "bin"),
            src=self.source_folder,
        )
        old_target_filename = os.path.join(self.package_folder, "bin", self._bazel_filename)
        new_target_filename = os.path.join(self.package_folder, "bin", "bazel" + self._program_suffix)
        rename(self, old_target_filename, new_target_filename)
        self._chmod_plus_x(new_target_filename)

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        # TODO: Legacy, to be removed on Conan 2.0
        bin_folder = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_folder)
