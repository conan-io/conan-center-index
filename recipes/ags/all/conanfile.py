import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import collect_libs, copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, msvc_runtime_flag, check_min_vs
from conan.tools.microsoft.visual import vs_ide_version
from conan.tools.scm import Version

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

    def layout(self):
        basic_layout(self, src_folder="src")

    @property
    def _supported_archs(self):
        return ["x86_64", "x86"]

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration(f"ags doesn't support OS: {self.settings.os}.")
        if not is_msvc(self):
            raise ConanInvalidConfiguration(
                f"ags doesn't support compiler: {self.settings.compiler} on OS: {self.settings.os}."
            )
        check_min_vs(self, 190)
        if Version(self.version) < "6.1.0" and check_min_vs(self, 193, raise_invalid=True):
            raise ConanInvalidConfiguration(f"Visual Studio 2019 or older is required for v{self.version}")
        if self.settings.arch not in self._supported_archs:
            raise ConanInvalidConfiguration(f"ags doesn't support arch: {self.settings.arch}")
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    @property
    def _vs_ide_year(self):
        return {
            "14": "2015",
            "15": "2017",
            "16": "2019",
            "17": "2022",
        }[str(vs_ide_version(self))]

    @property
    def _win_arch(self):
        return {
            "x86_64": "x64",
            "x86": "x86",
        }[str(self.settings.arch)]

    def package(self):
        ags_lib_path = os.path.join(self.source_folder, "ags_lib")
        copy(self, "LICENSE.txt",
             dst=os.path.join(self.package_folder, "licenses"),
             src=ags_lib_path)
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(ags_lib_path, "inc"))

        if is_msvc(self):
            win_arch = self._win_arch
            if self.options.get_safe("shared"):
                copy(self, f"amd_ags_{win_arch}.dll",
                     dst=os.path.join(self.package_folder, "bin"),
                     src=os.path.join(ags_lib_path, "lib"))
                copy(self, f"amd_ags_{win_arch}.lib",
                     dst=os.path.join(self.package_folder, "lib"),
                     src=os.path.join(ags_lib_path, "lib"))
            else:
                static_lib = f"amd_ags_{win_arch}_{self._vs_ide_year}_{msvc_runtime_flag(self)}.lib"
                copy(self, static_lib,
                     dst=os.path.join(self.package_folder, "lib"),
                     src=os.path.join(ags_lib_path, "lib"))

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
