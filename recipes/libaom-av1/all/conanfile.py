from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class LibaomAv1Conan(ConanFile):
    name = "libaom-av1"
    description = "AV1 Codec Library"
    topics = ("av1", "codec", "video", "encoding", "decoding")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://aomedia.googlesource.com/aom"
    license = "BSD-2-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "assembly": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "assembly": False,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "6",
        }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ("x86", "x86_64"):
            del self.options.assembly

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        # Check compiler version
        compiler = str(self.info.settings.compiler)
        compiler_version = Version(self.info.settings.compiler.version)
        minimum_version = self._compilers_minimum_version.get(compiler, False)
        if minimum_version and compiler_version < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires a {compiler} version >= {compiler_version}",
            )

    def build_requirements(self):
        if self.options.get_safe("assembly", False):
            self.tool_requires("nasm/2.15.05")
        if self._settings_build.os == "Windows":
            self.tool_requires("strawberryperl/5.30.0.1")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=Version(self.version) >= "3.3.0")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_EXAMPLES"] = False
        tc.variables["ENABLE_TESTS"] = False
        tc.variables["ENABLE_DOCS"] = False
        tc.variables["ENABLE_TOOLS"] = False
        if not self.options.get_safe("assembly", False):
            # make non-assembly build
            tc.variables["AOM_TARGET_CPU"] = "generic"
        # libyuv is used for examples, tests and non-essential 'dump_obu' tool so it is disabled
        # required to be 1/0 instead of False
        tc.variables["CONFIG_LIBYUV"] = 0
        # webm is not yet packaged
        tc.variables["CONFIG_WEBM_IO"] = 0
        tc.generate()
        env = VirtualBuildEnv(self)
        env.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "aom")
        self.cpp_info.libs = ["aom"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "m"]

        self.cpp_info.names["pkg_config"] = "aom"
