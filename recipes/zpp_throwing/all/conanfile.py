from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class ZppThrowingConan(ConanFile):
    name = "zpp_throwing"
    description = "Using coroutines to implement C++ exceptions for freestanding environments"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/eyalz800/zpp_throwing"
    topics = ("coroutines", "exceptions", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "17",
            "msvc": "193",
            "gcc": "11",
            "clang": "12",
            "apple-clang": "13.1",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        # TODO: currently msvc isn't suppported
        # see https://github.com/eyalz800/zpp_throwing/issues/7
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support MSVC (yet). See https://github.com/eyalz800/zpp_throwing/issues/7")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        compiler = str(self.settings.compiler)
        version = str(self.settings.compiler.version)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler ({compiler}-{version}) does not support.",
            )

        if self.settings.compiler == "clang" and Version(self.settings.compiler.version) < "14" and self.settings.compiler.get_safe("libcxx") != "libc++":
            raise ConanInvalidConfiguration(f"{self.ref} requires libc++ with 'coroutines' supported on your compiler.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=self.source_folder,
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.compiler == "clang" and self.settings.compiler.get_safe("libcxx") == "libc++":
            self.cpp_info.cxxflags.append("-fcoroutines-ts")

