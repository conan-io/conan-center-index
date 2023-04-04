from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMake, CMakeToolchain, CMakeDeps
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, apply_conandata_patches, export_conandata_patches
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.55.0"


class CcacheConan(ConanFile):
    name = "ccache"
    description = (
        "Ccache (or “ccache”) is a compiler cache. It speeds up recompilation "
        "by caching previous compilations and detecting when the same "
        "compilation is being done again."
    )
    license = "GPL-3.0-or-later"
    topics = ("compiler-cache", "recompilation", "cache", "compiler")
    homepage = "https://ccache.dev"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "redis_storage_backend": [True, False],
    }
    default_options = {
        "redis_storage_backend": True,
    }

    @property
    def _min_cppstd(self):
        if Version(self.version) > "4.7":
            return "17"
        else:
            return "17" if is_msvc(self) else "14"

    @property
    def _compilers_minimum_version(self):
        if Version(self.version) > "4.7":
            return {
                "gcc": "8",
                "clang": "9",
                "apple-clang": "11",
                "Visual Studio": "16.2",
                "msvc": "192",
            }
        else:
            return {
                "gcc": "6",
                "clang": "6",
                "apple-clang": "10",
                "Visual Studio": "15.7" if Version(self.version) < "4.6" else "16.2",
                "msvc": "191" if Version(self.version) < "4.6" else "192"
            }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("zstd/1.5.2")
        if self.options.redis_storage_backend:
            self.requires("hiredis/1.1.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                "{} requires C++{}, which your compiler does not support.".format(self.name, self._min_cppstd)
            )

    def package_id(self):
        del self.info.settings.compiler

    def build_requirements(self):
        self.tool_requires("cmake/3.25.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["REDIS_STORAGE_BACKEND"] = self.options.redis_storage_backend
        tc.variables["HIREDIS_FROM_INTERNET"] = False
        tc.variables["ENABLE_DOCUMENTATION"] = False
        tc.variables["ENABLE_TESTING"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("hiredis", "cmake_target_name", "HIREDIS::HIREDIS")
        deps.set_property("hiredis", "cmake_find_mode", "module")
        deps.set_property("zstd", "cmake_target_name", "ZSTD::ZSTD")
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "*GPL-*.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
        self.cpp_info.includedirs = []
