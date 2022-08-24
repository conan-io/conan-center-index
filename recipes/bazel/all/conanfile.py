from conan import ConanFile, tools
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
        return "bazel-{}-{}-{}{}".format(self.version, platform, self.settings.arch, self._program_suffix)

    def validate(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Only amd64 is supported for this package.")
        if self.settings.os not in ["Linux", "Macos", "Windows"]:
            raise ConanInvalidConfiguration("Only Linux, Windows and OSX are supported for this package.")

    def build(self):
        for source in self.conan_data["sources"][self.version]:
            url = source["url"]
            filename = url[url.rfind("/") + 1:]
            if filename in ["LICENSE", self._bazel_filename]:
                tools.files.download(self, url, filename)
                tools.check_sha256(filename, source["sha256"])

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses")
        self.copy(pattern=self._bazel_filename, dst="bin")
        old_target_filename = os.path.join(self.package_folder, "bin", self._bazel_filename)
        new_target_filename = os.path.join(self.package_folder, "bin", "bazel" + self._program_suffix)
        tools.files.rename(self, old_target_filename, new_target_filename)
        self._chmod_plus_x(new_target_filename)

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable with : {0}".format(bin_path))
        self.env_info.path.append(bin_path)
