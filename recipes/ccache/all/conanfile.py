from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.33.0"


class CcacheConan(ConanFile):
    name = "ccache"
    description = (
        "Ccache (or “ccache”) is a compiler cache. It speeds up recompilation "
        "by caching previous compilations and detecting when the same "
        "compilation is being done again."
    )
    license = "GPL-3.0-or-later"
    topics = ("ccache", "compiler-cache", "recompilation")
    homepage = "https://ccache.dev"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "redis_storage_backend": [True, False],
    }
    default_options = {
        "redis_storage_backend": True,
    }

    generators = "cmake", "cmake_find_package_multi"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _min_cppstd(self):
        return "17" if self._is_msvc else "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "6",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15.7" if tools.Version(self.version) < "4.6" else "16.2",
        }

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def requirements(self):
        self.requires("zstd/1.5.2")
        if self.options.redis_storage_backend:
            self.requires("hiredis/1.0.2")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)

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
        if hasattr(self, "settings_build") and tools.cross_building(self) and \
           self.settings.os == "Macos" and self.settings.arch == "armv8":
            self.build_requires("cmake/3.22.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["REDIS_STORAGE_BACKEND"] = self.options.redis_storage_backend
        cmake.definitions["ENABLE_DOCUMENTATION"] = False
        cmake.definitions["ENABLE_TESTING"] = False
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("GPL-*.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
