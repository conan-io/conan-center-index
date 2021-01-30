import os

from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class ProtobufCompilerConan(ConanFile):
    name = "protobuf-compiler"
    description = "Protocol Buffers Compiler"
    topics = (
        "conan", "protobuf", "protocol-buffers",
        "protocol-compiler", "serialization", "rpc", "protocol-compiler"
    )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/protocolbuffers/protobuf"
    license = "BSD-3-Clause"
    short_paths = True
    no_copy_source = True
    settings = {
        "os_build": ["Windows", "Linux", "Macos"],
        "arch_build": ["x86", "x86_64", "ppc64le", "armv8"]
    }

    def configure(self):
        # TODO other binares available: win32, linux-x86_32, linux-aarch_64, linux-ppcle_64, linux-s390x
        # TODO for suporting other archs, conandata.yml must be extended too
        valid_combinations = {
            "Windows": ["x86_64"],  # TODO add "x86" if required
            "Linux": ["x86_64"],  # TODO add "x86", "armv8", "ppc64le" if required
            "Macos": ["x86_64"]
        }
        if str(self.settings.arch_build) not in valid_combinations[str(self.settings.os_build)]:
            raise ConanInvalidConfiguration("No binaries available for {} architecture {}".format(
                self.settings.os_build, self.settings.arch_build,
            ))

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tarballs = self.conan_data["sources"][self.version]
        tools.get(**tarballs[str(self.settings.os_build)], destination=self._source_subfolder)

    def build(self):
        pass # no build, but please also no warnings

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == 'posix':
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package(self):
        self.copy(pattern="*", dst=".", src=self._source_subfolder, keep_path=True, symlinks=True)
        self.copy(pattern="readme.txt", dst="licenses", src=self._source_subfolder)
        os.unlink(os.path.join(self.package_folder, "readme.txt"))
        self._chmod_plus_x(os.path.join(self.package_folder, "bin", "protoc"))

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        # TODO add include directories for proto files? seems not to be required!
