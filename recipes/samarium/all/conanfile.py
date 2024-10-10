import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain, CMakeDeps
from conan.tools.files import copy, get, save
from conan.tools.scm import Version

required_conan_version = ">=1.47.0"


class SamariumConan(ConanFile):
    name = "samarium"
    description = "2-D physics simulation library"
    homepage = "https://jjbel.github.io/samarium/"
    url = "https://github.com/conan-io/conan-center-index/"
    license = "MIT"
    topics = ("cpp20", "physics", "2d", "simulation")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "13",
            "apple-clang": "13",
            "msvc": "192",
            "Visual Studio": "16",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # samarium relies on stb_image_write.h being instantiated in SFML with STB_IMAGE_WRITE_IMPLEMENTATION,
        # but it is not built with --whole-archive, so some symbols expected by samarium are not found.
        # Adding STB_IMAGE_WRITE_IMPLEMENTATION in samarium would lead to issues on apple-clang and MSVC due to multiple definitions.
        self.options["sfml"].shared = False

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Undefined symbols for architecture arm64: "void fmt::v10::detail::vformat_to..." when using sm::print
        self.requires("fmt/10.2.1", transitive_headers=True, transitive_libs=True)
        # Undefined symbols for architecture arm64: "sf::Keyboard::isKeyPressed(sf::Keyboard::Key)"
        # when using inlined is_key_pressed function
        self.requires("sfml/2.6.1", transitive_headers=True, transitive_libs=True)
        self.requires("range-v3/cci.20240905", transitive_headers=True)
        self.requires("stb/cci.20230920")
        self.requires("tl-expected/20190710", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.dependencies["sfml"].options.shared:
            raise ConanInvalidConfiguration("SFML dependency must be built as a static library")

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["RUN_CONAN"] = False
        tc.cache_variables["BUILD_UNIT_TESTS"] = False
        tc.cache_variables["BUILD_EXAMPLES"] = False
        tc.cache_variables["BUILD_DOCS"] = False
        tc.cache_variables["BUILD_DOCS_TARGET"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        # Force-disable all tests
        save(self, os.path.join(self.source_folder, "test", "CMakeLists.txt"), "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["samarium"]
