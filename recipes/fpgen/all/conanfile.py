import os

from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration


class FpgenConan(ConanFile):
    name = "fpgen"
    description = " Functional programming in C++ using C++20 coroutines."
    license = ["MPL2"]
    topics = (
        "generators",
        "coroutines",
        "c++20",
        "header-only",
        "functional-programming",
        "functional",
    )
    homepage = "https://github.com/jay-tux/fpgen/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "arch", "os", "compiler", "build_type"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "13",
        }

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            destination=self._source_subfolder,
            strip_root=True,
        )

    def validate(self):
        if self.settings.compiler == "clang" and "clang" not in str(self.version):
            raise ConanInvalidConfiguration(
                f"Use '{self.version}-clang' for Clang support."
            )

        if (
            self.settings.compiler == "clang"
            and not self.settings.compiler.libcxx == "libc++"
        ):
            raise ConanInvalidConfiguration(
                f"Use 'compiler.libcxx=libc++' for {self.name} on Clang."
            )

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False
        )
        if not minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} is currently not available for your compiler."
            )
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires C++20, which your compiler does not support."
            )

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(
            pattern="*.hpp",
            dst=os.path.join("include", "fpgen"),
            src=self._source_subfolder,
            keep_path=False,
        )

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join("include", "fpgen"))
