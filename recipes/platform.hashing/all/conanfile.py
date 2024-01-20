from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
import os


required_conan_version = ">=1.52.0"

class PlatformInterfacesConan(ConanFile):
    name = "platform.hashing"
    description = "platform.hashing is one of the libraries of the LinksPlatform modular framework, " \
                  "which contains std::hash specializations for:\n" \
                  " - trivial and standard-layout types\n" \
                  " - types constrained by std::ranges::range\n" \
                  " - std::any"
    license = "LGPL-3.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/linksplatform/Hashing"
    topics = ("linksplatform", "cpp20", "hashing", "any", "ranges", "native", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _internal_cpp_subfolder(self):
        return os.path.join(self.source_folder, "cpp", "Platform.Hashing")

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10",
            "Visual Studio": "16",
            "msvc": "192",
            "clang": "14",
            "apple-clang": "14"
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) >= "0.5.6":
            self.requires("cpuinfo/cci.20220228", transitive_headers=True)
        elif Version(self.version) >= "0.5.0":
            self.requires("cpu_features/0.9.0", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.arch in ("x86", ):
            raise ConanInvalidConfiguration(f"{self.ref} does not support arch={self.settings.arch}")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder
        )
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "cpp", "Platform.Hashing")
        )

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
        if is_msvc(self):
            if Version(self.version) >= "0.5.0":
                arch_macros = {
                    "x86_64": "_X86_64_",
                    "armv8": "_AARCH_",
                }.get(str(self.settings.arch), "")
                self.cpp_info.defines.append(arch_macros)
        else:
            suggested_flags = {
                "x86_64": "-march=haswell",
                "armv7": "-march=armv7",
                "armv8": "-march=armv8-a",
            }.get(str(self.settings.arch), "")
            self.conf_info.define("user.platform_hashing:suggested_flags", suggested_flags)

            if "-march" not in "{} {}".format(os.environ.get("CPPFLAGS", ""), os.environ.get("CXXFLAGS", "")):
                self.output.warning("platform.hashing needs to have `-march=ARCH` added to CPPFLAGS/CXXFLAGS. "
                                f"A suggestion is available in dependencies[{self.name}].conf_info.get(\"user.platform_hashing:suggested_flags\")")
