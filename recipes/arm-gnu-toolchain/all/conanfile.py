from conan import ConanFile
from conan.tools.files import get, copy, download
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.60.2"


class ArmGnuToolchain(ConanFile):
    name = "arm-gnu-toolchain"
    license = ("GPL-3.0-only", "GPL-2.0-only", "BSD-3-Clause",
               "BSD-2-Clause-FreeBSD", "AGPL-3.0-only", "BSD-2-Clause")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads"
    description = ("Conan installer for the GNU Arm Embedded Toolchain")
    topics = ("gcc", "compiler", "embedded", "arm", "cortex", "cortex-m",
              "cortex-m0", "cortex-m0+", "cortex-m1", "cortex-m3", "cortex-m4",
              "cortex-m4f", "cortex-m7", "cortex-m23", "cortex-m55",
              "cortex-m35p", "cortex-m33")
    settings = "os", "arch", 'compiler', 'build_type'
    exports_sources = "toolchain.cmake"
    package_type = "application"
    short_paths = True

    @property
    def download_info(self):
        version = self.version
        conan_os = str(self._settings_build.os)
        arch = str(self._settings_build.arch)
        return self.conan_data.get("sources", {}).get(version, {}).get(conan_os, {}).get(arch)

    @property
    def license_url(self):
        # License URL found from the "EULA" button on the
        # https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads
        # web page.
        if self.version == "11.3.0":
            return "https://developer.arm.com/GetEula?Id=ff19df33-da82-491a-ab50-c605d4589a26"
        if self.version == "12.2.1":
            return "https://developer.arm.com/GetEula?Id=2821586b-44d0-4e75-a06d-4279cd97eaae"
        if self.version == "12.3.1":
            return "https://developer.arm.com/GetEula?Id=aa3d692d-bc99-4c8c-bce2-588181ddde13"
        else:
            # This should only happen if the toolchain is packaged with its
            # license file.
            return None

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        supported_build_operating_systems = ["Linux", "Macos", "Windows"]
        if not self._settings_build.os in supported_build_operating_systems:
            raise ConanInvalidConfiguration(
                f"The build os '{self._settings_build.os}' is not supported. "
                "Pre-compiled binaries are only available for "
                f"{supported_build_operating_systems}."
            )

        supported_build_architectures = {
            "Linux": ["armv8", "x86_64"],
            "Macos": ["armv8", "x86_64"],
            "Windows": ["x86_64"],
        }

        if (
            not self._settings_build.arch
            in supported_build_architectures[str(self._settings_build.os)]
        ):
            build_os = str(self._settings_build.os)
            raise ConanInvalidConfiguration(
                f"The build architecture '{self._settings_build.arch}' "
                f"is not supported for {self._settings_build.os}. "
                "Pre-compiled binaries are only available for "
                f"{supported_build_architectures[build_os]}."
            )

        compiler_name = str(self.settings.compiler)
        if compiler_name != "gcc":
            raise ConanInvalidConfiguration(
                "The compiler must be set to gcc to use this toolchain.")

        compiler_version = str(self.settings.compiler.version)
        supported_compiler_versions = ["11", "11.3", "12", "12.2", "12.3"]
        if compiler_version not in supported_compiler_versions:
            raise ConanInvalidConfiguration(
                "The compiler version must be one of the following: "
                f"{supported_compiler_versions}.")

        major_version = str(self.version).split(".")[0]
        major_compiler_settings_version = compiler_version.split(".")[0]
        if major_version != major_compiler_settings_version:
            raise ConanInvalidConfiguration(
                f"The compiler version [{major_compiler_settings_version}] and "
                f"package version [{major_version}] must be the same.")

    def source(self):
        pass

    def build(self):
        if self.license_url:
            download(self, self.license_url, "LICENSE", verify=False)

        get(self,
            **self.conan_data["sources"][self.version][str(self._settings_build.os)][str(self._settings_build.arch)],
            destination=self.build_folder, strip_root=True)

    def package(self):
        destination = os.path.join(self.package_folder, "bin")

        copy(self, pattern="arm-none-eabi/*", src=self.build_folder,
             dst=destination, keep_path=True)
        copy(self, pattern="bin/*", src=self.build_folder,
             dst=destination, keep_path=True)
        copy(self, pattern="include/*", src=self.build_folder,
             dst=destination, keep_path=True)
        copy(self, pattern="lib/*", src=self.build_folder,
             dst=destination, keep_path=True)
        copy(self, pattern="libexec/*", src=self.build_folder,
             dst=destination, keep_path=True)
        copy(self, pattern="share/*", src=self.build_folder,
             dst=destination, keep_path=True)

        license_dir = os.path.join(self.package_folder, "licenses/")
        copy(self, pattern="LICENSE*", src=self.build_folder,
             dst=license_dir, keep_path=True)

        resource_dir = os.path.join(self.package_folder, "res/")
        copy(self, pattern="toolchain.cmake", src=self.build_folder,
             dst=resource_dir, keep_path=True)

    def package_info(self):
        self.cpp_info.includedirs = []

        bin_folder = os.path.join(self.package_folder, "bin/bin")
        self.cpp_info.bindirs = [bin_folder]
        self.buildenv_info.append_path("PATH", bin_folder)

        self.conf_info.define(
            "tools.cmake.cmaketoolchain:system_name", "Generic")
        self.conf_info.define(
            "tools.cmake.cmaketoolchain:system_processor", "ARM")
        self.conf_info.define("tools.build.cross_building:can_run", False)
        self.conf_info.define("tools.build:compiler_executables", {
            "c": "arm-none-eabi-gcc",
            "cpp": "arm-none-eabi-g++",
            "asm": "arm-none-eabi-as",
        })

        f = os.path.join(self.package_folder, "res/toolchain.cmake")
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", f)
