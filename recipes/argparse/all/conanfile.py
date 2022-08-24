from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class ArgparseConan(ConanFile):
    name = "argparse"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/p-ranav/argparse"
    topics = ("argparse", "argument", "parsing")
    license = "MIT"
    description = "Argument Parser for Modern C++"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _compiler_required_cpp17(self):
        return {
            "gcc": "7" if tools.Version(self.version) <= "2.1" else "8",
            "clang": "5" if tools.Version(self.version) <= "2.1" else "7",
            # trantor/2.5 uses [[maybe_unused]] in range-based for loop
            # Visual Studio 15 doesn't support it:
            # https://developercommunity.visualstudio.com/t/compiler-bug-on-parsing-maybe-unused-in-range-base/209488
            "Visual Studio": "15" if tools.Version(self.version) < "2.5" else "16",
            "apple-clang": "10",
        }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def build(self):
        self._patch_sources()

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            tools.build.check_min_cppstd(self, self, "17")
        try:
            minimum_required_compiler_version = self._compiler_required_cpp17[str(self.settings.compiler)]
            if tools.Version(self.settings.compiler.version) < minimum_required_compiler_version:
                raise ConanInvalidConfiguration("This package requires c++17 support. The current compiler does not support it.")
        except KeyError:
            self.output.warn("This recipe has no support for the current compiler. Please consider adding it.")

        if tools.Version(self.version) > "2.1" and self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libstdc++":
            raise ConanInvalidConfiguration("This recipe does not permit >2.1 with clang and stdlibc++. There may be an infrastructure issue in CCI.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if tools.Version(self.version) <= "2.1":
            self.copy("*.hpp", src=os.path.join(self._source_subfolder, "include"), dst=os.path.join("include", "argparse"))
        else:
            self.copy("*.hpp", src=os.path.join(self._source_subfolder, "include"), dst="include")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "argparse")
        self.cpp_info.set_property("cmake_target_name", "argparse::argparse")
        self.cpp_info.set_property("pkg_config_name", "argparse")
        if tools.Version(self.version) <= "2.1":
            self.cpp_info.includedirs.append(os.path.join("include", "argparse"))
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
