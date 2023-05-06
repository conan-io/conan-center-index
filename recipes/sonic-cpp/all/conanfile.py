from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.53.0"

class SonicCppConan(ConanFile):
    name = "sonic-cpp"
    description = "A fast JSON serializing & deserializing library, accelerated by SIMD."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bytedance/sonic-cpp"
    topics = ("json", "parser", "writer", "serializer", "deserializer", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _min_cppstd(self):
        return 11

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.compiler.cppstd and str(self.settings.compiler.cppstd) < "17":
            self.requires("string-view-lite/1.7.0", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        if self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration(f"{self.ref} support x86, x86_64 only.")

        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support MSVC now.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        if self.settings.compiler in ["gcc", "clang"]:
            self.cpp_info.cxxflags.extend(["-mavx2", "-mpclmul"])
