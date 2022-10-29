from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class ArgparseConan(ConanFile):
    name = "argparse"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/p-ranav/argparse"
    topics = ("argparse", "argument", "parsing")
    license = "MIT"
    description = "Argument Parser for Modern C++"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7" if Version(self.version) <= "2.1" else "8",
            "clang": "5" if Version(self.version) <= "2.1" else "7",
            # trantor/2.5 uses [[maybe_unused]] in range-based for loop
            # Visual Studio 15 doesn't support it:
            # https://developercommunity.visualstudio.com/t/compiler-bug-on-parsing-maybe-unused-in-range-base/209488
            "Visual Studio": "15" if Version(self.version) < "2.5" else "16",
            "msvc": "191" if Version(self.version) < "2.5" else "192",
            "apple-clang": "10",
        }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

        if Version(self.version) > "2.1" and self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libstdc++":
            raise ConanInvalidConfiguration("This recipe does not permit >2.1 with clang and stdlibc++. There may be an infrastructure issue in CCI.")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if Version(self.version) <= "2.1":
            include_dst = os.path.join(self.package_folder, "include", "argparse")
        else:
            include_dst = os.path.join(self.package_folder, "include")
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=include_dst)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "argparse")
        self.cpp_info.set_property("cmake_target_name", "argparse::argparse")
        self.cpp_info.set_property("pkg_config_name", "argparse")
        if Version(self.version) <= "2.1":
            self.cpp_info.includedirs.append(os.path.join("include", "argparse"))
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
