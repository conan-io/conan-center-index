import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import collect_libs, copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, check_min_vs
from conan.tools.microsoft.visual import msvc_version_to_vs_ide_version

required_conan_version = ">=1.52.0"


class AGSConan(ConanFile):
    name = "ags"
    description = (
        "The AMD GPU Services (AGS) library provides software developers with the ability to query AMD GPU "
        "software and hardware state information that is not normally available through standard operating "
        "systems or graphics APIs."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/GPUOpen-LibrariesAndSDKs/AGS_SDK"
    topics = ("amd", "gpu", "header-only")

    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _supported_archs(self):
        return ["x86_64", "x86"]

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration(f"ags doesn't support OS: {self.settings.os}.")
        if not is_msvc(self):
            raise ConanInvalidConfiguration(
                f"ags doesn't support compiler: {self.settings.compiler} on OS: {self.settings.os}."
            )
        check_min_vs(self, 190)
        if self.settings.arch not in self._supported_archs:
            raise ConanInvalidConfiguration(f"ags doesn't support arch: {self.settings.arch}")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _convert_msvc_version_to_vs_version(self, msvc_version):
        if int(msvc_version) > 100:
            msvc_version = msvc_version_to_vs_ide_version(msvc_version)
        vs_versions = {
            "14": "2015",
            "15": "2017",
            "16": "2019",
            "17": "2022",
        }
        return vs_versions[str(msvc_version)]

    def _convert_arch_to_win_arch(self, arch):
        win_arch = {
            "x86_64": "x64",
            "x86": "x86",
        }
        return win_arch[str(arch)]

    def package(self):
        ags_lib_path = os.path.join(self.source_folder, "ags_lib")
        copy(self, "LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=ags_lib_path)
        copy(self, "*.h", dst=os.path.join(self.package_folder, "include"), src=os.path.join(ags_lib_path, "inc"))

        if is_msvc(self):
            win_arch = self._convert_arch_to_win_arch(self.settings.arch)
            if self.options.shared:
                copy(self, f"amd_ags_{win_arch}.dll",
                    dst=os.path.join(self.package_folder, "bin"),
                    src=os.path.join(ags_lib_path, "lib"))
                copy(self, f"amd_ags_{win_arch}.lib",
                    dst=os.path.join(self.package_folder, "lib"),
                    src=os.path.join(ags_lib_path, "lib"))
            else:
                vs_version = self._convert_msvc_version_to_vs_version(self.settings.compiler.version)
                static_lib = f"amd_ags_{win_arch}_{vs_version}_{msvc_runtime_flag(self)}.lib"
                copy(self, static_lib,
                    dst=os.path.join(self.package_folder, "lib"),
                    src=os.path.join(ags_lib_path, "lib"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
