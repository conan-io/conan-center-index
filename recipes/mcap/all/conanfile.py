from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.52.0"

class McapConan(ConanFile):
    name = "mcap"
    description = (
        "MCAP is a modular, performant, and serialization-agnostic container file format for pub/sub messages, "
        "primarily intended for use in robotics applications."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/foxglove/mcap"
    topics = ("serialization", "deserialization", "recording")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_lz4": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_lz4": True,
        "with_zstd": True,
    }
    implements = ["auto_shared_fpic"]

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "191",
            "gcc": "7",
            "clang": "9",
            "apple-clang": "12",
        }

    @property
    def _source_package_path(self):
        return os.path.join(self.source_folder, "cpp", "mcap")

    def configure(self):
        if Version(self.version) < "0.3.0":
            self.license = "Apache-2.0"

    def export_sources(self):
        # Upstream library does not ship with a build system.
        export_source_path = os.path.join(self.export_sources_folder, "src", "cpp", "mcap")
        copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=export_source_path)
        copy(self, "mcap.cpp", src=self.recipe_folder, dst=export_source_path)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_lz4:
            self.requires("lz4/[>=1.9.4]")
        if self.options.with_zstd:
            self.requires("zstd/[>=1.5.5]")
        if Version(self.version) < "0.1.1":
            self.requires("fmt/[>=9.1.0]")

    def validate(self):
        if Version(self.version) < "0.1.1" and is_msvc(self):
            raise ConanInvalidConfiguration("Visual Studio compiler has been supported since 0.1.1")

        if Version(self.version) < "0.7.0" and self.options.shared:
            raise ConanInvalidConfiguration("Shared library has been supported since 0.7.0")

        if Version(self.version) < "1.1.1" and (not self.options.with_lz4 or not self.options.with_zstd):
            raise ConanInvalidConfiguration("lz4 and zstd are optional since 1.1.1")

        check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["MCAP_COMPRESSION_LZ4"] = bool(self.options.with_lz4)
        tc.variables["MCAP_COMPRESSION_ZSTD"] = bool(self.options.with_zstd)
        tc.generate()

        deps = CMakeDeps(self)
        if self.options.with_zstd:
            deps.set_property("zstd", "cmake_target_name", "zstd::zstd")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=self._source_package_path)
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self._source_package_path)
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.components["mcap"].set_property("cmake_target_name", "mcap::mcap")
        self.cpp_info.components["mcap"].set_property("pkg_config_name", "mcap")
        self.cpp_info.components["mcap"].libs = ["mcap"]
        if not self.options.shared:
            self.cpp_info.components["mcap"].defines.append("MCAP_PUBLIC=")
        if self.options.with_lz4:
            self.cpp_info.components["mcap"].requires.append("lz4::lz4")
        else:
            self.cpp_info.components["mcap"].defines.append("MCAP_COMPRESSION_NO_LZ4=1")
        if self.options.with_zstd:
            self.cpp_info.components["mcap"].requires.append("zstd::zstd")
        else:
            self.cpp_info.components["mcap"].defines.append("MCAP_COMPRESSION_NO_ZSTD=1")
