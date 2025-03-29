from conan import ConanFile
from conan.tools.files import copy, download, rename
import os

class OpenIAPConan(ConanFile):
    name = "openiap"
    version = "0.0.1"
    license = "MPL-2.0"
    url = "https://github.com/openiap/rustapi"
    homepage = "https://openiap.io"
    description = "Client library for OpenCore, header file and prebuilt binaries"
    settings = "os", "arch"
    no_copy_source = False

    def validate(self):
        """Ensure that we only download the necessary binary."""
        supported_files = {
            ("Linux", "x86_64"): "libopeniap-linux-x64.so",
            ("Linux", "armv8"): "libopeniap-linux-arm64.so",
            ("Macos", "x86_64"): "libopeniap-macos-x64.dylib",
            ("Macos", "armv8"): "libopeniap-macos-arm64.dylib",
            ("Windows", "x86_64"): "openiap-windows-x64.dll",
            ("Windows", "x86"): "openiap-windows-i686.dll",
        }

        target = (str(self.settings.os), str(self.settings.arch))
        if target not in supported_files:
            raise ConanInvalidConfiguration(f"Unsupported OS/Arch: {target}")

        self.binary_filename = supported_files[target]

    def source(self):
        """Download the correct precompiled binary for the target system."""
        binaries = self.conan_data["sources"][self.version]

        lib_dir = os.path.join(self.source_folder, "lib")
        os.makedirs(lib_dir, exist_ok=True)
        include_dir = os.path.join(self.source_folder, "include")
        os.makedirs(include_dir, exist_ok=True)

        for source in binaries:
            url = source["url"]
            filename = os.path.basename(url)

            # Only download the required binary
            if filename == self.binary_filename or filename.endswith(".h"):
                print(f"Downloading {url}")
                download(self, url, filename, sha256=source["sha256"])

                if filename.endswith(".h"):
                    rename(self, src=filename, dst=os.path.join(self.source_folder, "include", filename))
                    print(f"as include/{filename}")
                else:
                    rename(self, src=filename, dst=os.path.join(self.source_folder, "lib", filename))
                    print(f"as lib/{filename}")

    def package(self):
        """Package the header file and precompiled libraries."""
        copy(self, "clib_openiap.h", src="include", dst=os.path.join(self.package_folder, "include"), keep_path=False)
        copy(self, "*", src="lib", dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        """Provide library linking information."""
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]

        # Expose the library file for linking
        if self.settings.os == "Linux":
            if self.settings.arch == "x86_64":
                self.cpp_info.libs = ["openiap-linux-x64"]
            elif self.settings.arch == "armv8":
                self.cpp_info.libs = ["openiap-linux-arm64"]
        elif self.settings.os == "Macos":
            if self.settings.arch == "x86_64":
                self.cpp_info.libs = ["openiap-macos-x64"]
            elif self.settings.arch == "armv8":
                self.cpp_info.libs = ["openiap-macos-arm64"]
        elif self.settings.os == "Windows":
            if self.settings.arch == "x86_64":
                self.cpp_info.libs = ["openiap-windows-x64"]
            elif self.settings.arch == "x86":
                self.cpp_info.libs = ["openiap-windows-i686"]

        # Fix: Make sure the include and lib paths are properly exposed
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs.append(os.path.join(self.package_folder, "lib"))
        self.cpp_info.includedirs.append(os.path.join(self.package_folder, "include"))

    def deploy(self):
        """Ensure the header and library files are copied into the build folder"""
        copy(self, "*", src=self.package_folder, dst=self.install_folder, keep_path=True)
