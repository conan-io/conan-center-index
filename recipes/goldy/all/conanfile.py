from conan import ConanFile
from conan.tools.files import copy, get, download, load
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=2.0"


class GoldyConan(ConanFile):
    name = "goldy"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/koubaa/goldy"
    description = "Modern GPU library with Slang shader support"
    topics = ("gpu", "graphics", "vulkan", "rendering", "slang")
    package_type = "shared-library"

    settings = "os", "arch", "compiler", "build_type"

    # Supported platforms for pre-built binaries
    _supported_platforms = {
        ("Windows", "x86_64"),
        ("Linux", "x86_64"),
        ("Macos", "x86_64"),
        ("Macos", "armv8"),
    }

    def export_sources(self):
        copy(self, "conandata.yml", src=self.recipe_folder, dst=self.export_sources_folder)

    def validate(self):
        key = (str(self.settings.os), str(self.settings.arch))
        if key not in self._supported_platforms:
            raise ConanInvalidConfiguration(
                f"{self.ref} does not support {self.settings.os} {self.settings.arch}. "
                f"Supported: Windows x86_64, Linux x86_64, macOS x86_64/armv8"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        # Download pre-built native library
        os_name = str(self.settings.os)
        arch = str(self.settings.arch)
        binary_info = self.conan_data["binaries"][self.version][os_name][arch]

        self.output.info(f"Downloading pre-built goldy_ffi for {os_name} {arch}...")

        filename = binary_info["url"].split("/")[-1]
        download(self, url=binary_info["url"], filename=filename, sha256=binary_info["sha256"])

        # Extract the archive
        if filename.endswith(".zip"):
            import zipfile
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall("binary")
        else:
            import tarfile
            with tarfile.open(filename, 'r:gz') as tar_ref:
                tar_ref.extractall("binary")

    def package(self):
        # Copy license
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

        # Copy headers from source
        copy(self, "*.h", src=os.path.join(self.source_folder, "cpp", "include"),
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "cpp", "include"),
             dst=os.path.join(self.package_folder, "include"))

        # Copy native library from pre-built binary
        binary_dir = os.path.join(self.build_folder, "binary")

        if self.settings.os == "Windows":
            copy(self, "goldy_ffi.dll", src=os.path.join(binary_dir, "lib"),
                 dst=os.path.join(self.package_folder, "bin"))
            copy(self, "goldy_ffi.dll.lib", src=os.path.join(binary_dir, "lib"),
                 dst=os.path.join(self.package_folder, "lib"))
            # Rename the import library
            old_path = os.path.join(self.package_folder, "lib", "goldy_ffi.dll.lib")
            new_path = os.path.join(self.package_folder, "lib", "goldy_ffi.lib")
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
        elif self.settings.os == "Linux":
            copy(self, "libgoldy_ffi.so", src=os.path.join(binary_dir, "lib"),
                 dst=os.path.join(self.package_folder, "lib"))
        elif self.settings.os == "Macos":
            copy(self, "libgoldy_ffi.dylib", src=os.path.join(binary_dir, "lib"),
                 dst=os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.libs = ["goldy_ffi"]

        self.cpp_info.set_property("cmake_file_name", "goldy")
        self.cpp_info.set_property("cmake_target_name", "goldy::goldy")

        if self.settings.os == "Windows":
            self.cpp_info.bindirs = ["bin"]
            # DLL needs to be in PATH at runtime
            self.runenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))

