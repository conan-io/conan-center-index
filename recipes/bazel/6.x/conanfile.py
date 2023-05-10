from conan import ConanFile
from conan.tools.files import check_sha256, copy, download, rename
from conan.errors import ConanInvalidConfiguration
import os


class BazelConan(ConanFile):
    name = "bazel"
    description = "Bazel is a fast, scalable, multi-language and extensible build system."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://bazel.build/"
    topics = ("test", "build", "automation")
    settings = "os", "arch"
    no_copy_source = True

    @property
    def _program_suffix(self):
        return ".exe" if self.settings.os == "Windows" else ""

    def _chmod_plus_x(self, name):
        os.chmod(name, os.stat(name).st_mode | 0o111)

    @property
    def _bazel_filename(self):
        platform = "darwin" if self.settings.os == "Macos" else str(self.settings.os).lower()
        fname = "bazel-{}-{}-{}{}".format(self.version, platform, self.settings.arch, self._program_suffix)
        return fname

    def validate(self):
        try:
            self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)]
        except KeyError:
            raise ConanInvalidConfiguration("Binaries for this combination of version/os/arch are not available")
    
    def build(self):
        executable = self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)]
        license = self.conan_data["sources"][self.version]["License"]

        for binary in (executable, license):
            url = binary["url"]
            checksum = binary["sha256"]
            filename = url[url.rfind("/") + 1:]
            download(self, url, filename)
            check_sha256(self, filename, checksum)

    def package(self):
        copy(self, pattern="LICENSE", src=self.build_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern=self._bazel_filename, src=self.build_folder, dst=os.path.join(self.package_folder, "bin"))
        old_target_filename = os.path.join(self.package_folder, "bin", self._bazel_filename)
        new_target_filename = os.path.join(self.package_folder, "bin", "bazel" + self._program_suffix)
        rename(self, old_target_filename, new_target_filename)
        self._chmod_plus_x(new_target_filename)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable with : {0}".format(bin_path))
        self.env_info.path.append(bin_path)
