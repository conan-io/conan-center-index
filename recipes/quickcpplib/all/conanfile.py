import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy, rmdir, rm
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.54.0"


class QuickcpplibCodeConan(ConanFile):
    name = "quickcpplib"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ned14/quickcpplib"
    description = "Eliminate all the tedious hassle when making state-of-the-art C++ 17 - 23 libraries!"
    topics = ("header-only", "common")
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"

    @property
    def _compiler_required_version(self):
        return {
            "gcc": "9",
            "clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    @property
    def _needs_span_lite(self):
        # TODO: Conan 1 only has check_min_cppstd, move to `valid_max_cppstd` when only Conan 2 is required
        try:
            check_min_cppstd(self, "20")
            return False
        except ConanInvalidConfiguration:
            return True

    @property
    def _min_cppstd(self):
        return "17"

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self._needs_span_lite:
            self.requires("span-lite/0.10.3")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            # To simplify library integration to CCI
            # we require C++17 to be dependency free.
            check_min_cppstd(self, self._min_cppstd)

        min_version = self._compiler_required_version.get(str(self.settings.compiler))
        if min_version:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(f"This package requires c++ {self._min_cppstd} support. The current compiler does not support it.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.ipp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "include", "quickcpplib", "byte"))
        rmdir(self, os.path.join(self.package_folder, "include", "quickcpplib", "boost"))
        rmdir(self, os.path.join(self.package_folder, "include", "quickcpplib", "optional"))
        rmdir(self, os.path.join(self.package_folder, "include", "quickcpplib", "span-lite"))
        rm(self, "allocator_testing.hpp", os.path.join(self.package_folder, "include", "quickcpplib"))
        copy(self, "Licence.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "quickcpplib")
        self.cpp_info.set_property("cmake_target_name", "quickcpplib::hl")

        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        if self._needs_span_lite:
            self.cpp_info.requires = ["span-lite::span-lite"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "pthread", "rt"]

        self.cpp_info.defines.append("QUICKCPPLIB_DISABLE_ABI_PERMUTATION")

        if self._needs_span_lite:
            self.cpp_info.defines.append("QUICKCPPLIB_USE_SYSTEM_SPAN_LITE=1")
        else:
            self.cpp_info.defines.append("QUICKCPPLIB_USE_STD_SPAN=1")

        self.cpp_info.defines.append("QUICKCPPLIB_USE_STD_BYTE=1")
        self.cpp_info.defines.append("QUICKCPPLIB_USE_STD_OPTIONAL=1")
