from conan import ConanFile
from conan.tools.files import get, copy, download
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=2.0.6"


class ArmGnuToolchain(ConanFile):
    name = "arm-gnu-toolchain"
    license = "GPL-3.0-only"
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
    build_policy = "missing"

    @property
    def download_info(self):
        version = self.version
        os = str(self._settings_build.os)
        arch = str(self._settings_build.arch)
        return self.conan_data.get("sources", {}).get(version, {}).get(os, {}).get(arch)

    @property
    def license_url(self):
        # All versions of arm-gnu-toolchain (previously called gnu-arm-embedded)
        # before 12.3.0 did NOT include their licenses in their package
        # releases. Instead they are a glob of multiple HTML licenses fused
        # together into a EULA.html file. This is a work around for those
        # versions.
        if self.version == "11.3.0" or self.version == "12.2.1":
            return "https://gist.githubusercontent.com/kammce/dc566a05f6ab2787ceef5b706012e7a2/raw/4cb8ab752d7c0f87cc074afa4e548a2be8766210/EULA.html"
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
                f"Pre-compiled binaries are only available for {supported_build_operating_systems}."
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
            raise ConanInvalidConfiguration(
                f"The build architecture '{self._settings_build.arch}' is not supported for {self._settings_build.os}. "
                f"Pre-compiled binaries are only available for {supported_build_architectures[str(self._settings_build.os)]}."
            )

    def source(self):
        pass

    def build(self):
        if self.license_url:
            download(self, self.license_url, "LICENSE", verify=False)

        destination_pico = os.path.join(self.build_folder, "picolibc/")
        destination_toolchain = os.path.join(self.build_folder, "toolchain/")

        if str(self.version) == "11.3.0":
            get(self,
                "https://github.com/picolibc/picolibc/releases/download/1.7.9/picolibc-1.7.9-11.3.rel1.zip", destination=destination_pico)
        elif str(self.version) == "12.2.1":
            get(self,
                "https://github.com/picolibc/picolibc/releases/download/1.8/picolibc-1.8-12.2.rel1.zip", destination=destination_pico)
        elif str(self.version) == "12.3.1":
            get(self,
                "https://github.com/picolibc/picolibc/releases/download/1.8.3/picolibc-1.8.3-12.3-rel1.zip",
                destination=destination_pico)

        get(self,
            **self.conan_data["sources"][self.version][str(self._settings_build.os)][str(self._settings_build.arch)], destination=destination_toolchain, strip_root=True)

    def package(self):
        picolibc_source = os.path.join(self.build_folder, "picolibc/")
        toolchain_source = os.path.join(self.build_folder, "toolchain/")
        destination = os.path.join(self.package_folder, "bin/")

        # Copy Picolibc files

        copy(self, pattern="arm-none-eabi/*", src=picolibc_source,
             dst=destination, keep_path=True)
        copy(self, pattern="bin/*", src=picolibc_source,
             dst=destination, keep_path=True)
        copy(self, pattern="include/*", src=picolibc_source,
             dst=destination, keep_path=True)
        copy(self, pattern="lib/*", src=picolibc_source,
             dst=destination, keep_path=True)
        copy(self, pattern="libexec/*", src=picolibc_source,
             dst=destination, keep_path=True)
        copy(self, pattern="share/*", src=picolibc_source,
             dst=destination, keep_path=True)

        # Copy Toolchain Files

        copy(self, pattern="arm-none-eabi/*", src=toolchain_source,
             dst=destination, keep_path=True)
        copy(self, pattern="bin/*", src=toolchain_source,
             dst=destination, keep_path=True)
        copy(self, pattern="include/*", src=toolchain_source,
             dst=destination, keep_path=True)
        copy(self, pattern="lib/*", src=toolchain_source,
             dst=destination, keep_path=True)
        copy(self, pattern="libexec/*", src=toolchain_source,
             dst=destination, keep_path=True)
        copy(self, pattern="share/*", src=toolchain_source,
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
