from conan import ConanFile
from conan.tools.files import get, copy, download
from conan.errors import ConanException, ConanInvalidConfiguration
import os
import pprint


required_conan_version = ">=1.50.0"


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
    short_paths = True

    @property
    def download_info(self):
        version = self.version
        os = str(self._settings_build.os)
        arch = str(self._settings_build.arch)
        return self.conan_data.get("sources", {}).get(version, {}).get(os, {}).get(arch)

    @property
    def license_url(self):
        return "https://gist.githubusercontent.com/kammce/dc566a05f6ab2787ceef5b706012e7a2/raw/4cb8ab752d7c0f87cc074afa4e548a2be8766210/EULA.html"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        if not self.download_info:
            raise ConanInvalidConfiguration(
                "This package is not available for this operating system and architecture.")

        if not hasattr(self, "settings_build"):
            raise ConanInvalidConfiguration(
                f"{self.name} must be used with a build profile.")

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

        pp = pprint.PrettyPrinter(indent=4)

        pp.pprint(str(self.settings.os))
        pp.pprint(str(self.settings.arch))
        pp.pprint(str(self._settings_build.arch))

        if (self.settings.os != "baremetal" and str(self.settings.arch) != str(self._settings_build.arch)):
            print("ARCH MISMATCH")
            # Update comment later if this works
            raise ConanInvalidConfiguration(
                f"This tool does not work when cross compiling to a target that is not 'baremetal'."
            )

    def source(self):
        pass

    def build(self):
        download(self, self.license_url, "LICENSE", verify=False)

        get(self,
            **self.conan_data["sources"][self.version][str(self._settings_build.os)][str(self._settings_build.arch)],
            strip_root=True)

    def package(self):
        destination = os.path.join(self.package_folder, "bin/")

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

        # float_abi = str(self.settings_target.arch.thumbv7em.float_abi)
        # float_abi = ""
        # processor = str(self.settings_target.arch.thumbv7em.processor)
        # c_flags = [f"-mfloat-abi={ float_abi }",
        #            f"-mcpu={ processor }",
        #            "-mthumb",
        #            "-ffunction-sections",
        #            "-fdata-sections",
        #            "-fno-exceptions",
        #            "-fno-rtti"]

        # self.conf_info.extend("tools.build:cflags", c_flags)
        # self.conf_info.extend("tools.build:cxxflags", c_flags)
        # self.conf_info.extend("tools.build:exelinkflags",
        #                       ["--specs=nano.specs",
        #                        "--specs=nosys.specs",
        #                        f"-mfloat-abi={ float_abi }",
        #                        f"-mcpu={processor}",
        #                        "-mthumb",
        #                        "-Wl,--gc-sections",
        #                        "-Wl,--print-memory-usage"])
