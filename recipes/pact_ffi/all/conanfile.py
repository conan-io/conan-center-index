from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.files import get, copy

import os

required_conan_version = ">=2.0.0"


class PactFFIConan(ConanFile):
    name = "pact_ffi"
    description = "Pact/Rust FFI bindings"
    url = "https://gitlab.prod.entos.sky/immerse-ui/libs/Pact"
    homepage = "https://github.com/pact-foundation/pact-reference"
    license = "MIT"
    settings = "os", "arch"
    no_copy_source = True
    topics = ("pact", "consumer-driven-contracts", "contract-testing", "mock-server")
    user = "sky"
    options = {
        "shared": [True, False]
    }
    default_options = {
        "shared": False
    }

    def validate(self):
        if not self.settings.arch == "x86_64":
            raise ConanInvalidConfiguration(f"Binary does not exist for architecture {self.settings.arch}")
        if self.settings.os not in ["Linux", "Macos"]:
            raise ConanInvalidConfiguration(f"Binary does not exist for OS {self.settings.os}")
        if self.settings.os == "Linux" and self.options.shared:
            raise ConanInvalidConfiguration(f"Shared library not supported on Linux")
        if self.settings.os == "Macos" and not self.options.shared:
            raise ConanInvalidConfiguration(f"Static library not supported on Macos")

    def build(self):
        data = self.conan_data["sources"][self.version]
        token = os.getenv("GITLAB_API_TOKEN") or os.getenv("CI_JOB_TOKEN")
        if token is None:
            raise ConanException("GITLAB_API_TOKEN or CI_JOB_TOKEN must be defined "
                                 "with a token with the permissions to read the Pact repository")
        get(
            self,
            data["url"],
            sha256=data["sha256"],
            strip_root=True,
            headers={"PRIVATE-TOKEN": token},
            filename=f"pact_ffi-{self.version}.tar.gz"
        )

    def package(self):
        subfolder = {
            "Linux": "linux-x86_64",
            "Macos": "mac-x86_64"
        }
        copy(self,
             "libpact*",
             os.path.join(self.build_folder, "lib", subfolder[str(self.settings.os)]),
             os.path.join(self.package_folder, "lib")
        )
        copy(self, "*.h", os.path.join(self.build_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.libs = ["pact_ffi"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
