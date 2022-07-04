import os

from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
from conans.tools import rmdir

required_conan_version = ">=1.33.0"


class Recipe(ConanFile):
    name = "metall"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/LLNL/metall"
    description = "Meta allocator for persistent memory"
    license = "MIT", "Apache-2.0"
    topics = "cpp", "allocator", "memory-allocator", "persistent-memory", "ecp", "exascale-computing"
    settings = "build_type", "compiler", "os", "arch"
    options = {
        # Disable freeing file space
        "disable_free_file_space": [True, False],
        # Disable small object cache
        "disable_small_object_cache": [True, False],
        # Use VM space aware algorithm in the bin directory
        "use_sorted_bin": [True, False],
        # Set the default VM reserve size (use the internally defined value if 0 is specified)
        "default_vm_reserve_size": "ANY",
        # Set the max segment size (use the internally defined value if 0 is specified)
        "max_segment_size": "ANY",
        # Set the initial segment size (use the internally defined value if 0 is specified)
        "initial_segment_size": "ANY",
        # Experimental: Use the anonymous map when creating a new map region
        "use_anonymous_new_map": [True, False],
        # Experimental: Build programs that require the NUMA policy library (numa.h)
        "build_numa": [True, False],
        # Experimental: Try to free the associated pages and file space when objects equal to or larger than that
        # is deallocated
        "free_small_object_size_hint": "ANY",
    }

    default_options = {
        "disable_free_file_space": False,
        "disable_small_object_cache": False,
        "use_sorted_bin": False,
        "default_vm_reserve_size": 0,
        "max_segment_size": 0,
        "initial_segment_size": 0,
        "use_anonymous_new_map": False,
        "build_numa": False,
        "free_small_object_size_hint": 0,
    }
    requires = "boost/1.79.0",

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self.folders.base_source,
                  strip_root=True)

    @property
    def _min_cppstd(self):
        return "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8.3",
            "clang": "9",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._min_cppstd)

        if self.settings.os not in ["Linux", "Macos"]:
            raise ConanInvalidConfiguration(
                "Metall requires some POSIX functionalities like mmap.")

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn(
                "{} {} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name,
                                                                                                     self.version))
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                "{} {} requires C++17, which your compiler does not support.".format(self.name, self.version))

    _cmake = None

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions['DISABLE_FREE_FILE_SPACE'] = self.options.disable_free_file_space
        self._cmake.definitions['DISABLE_SMALL_OBJECT_CACHE'] = self.options.disable_small_object_cache
        self._cmake.definitions['USE_SORTED_BIN'] = self.options.use_sorted_bin
        self._cmake.definitions['DEFAULT_VM_RESERVE_SIZE'] = self.options.default_vm_reserve_size
        self._cmake.definitions['MAX_SEGMENT_SIZE'] = self.options.max_segment_size
        self._cmake.definitions['INITIAL_SEGMENT_SIZE'] = self.options.initial_segment_size
        self._cmake.definitions['USE_ANONYMOUS_NEW_MAP'] = self.options.use_anonymous_new_map
        self._cmake.definitions['BUILD_NUMA'] = self.options.build_numa
        self._cmake.definitions['FREE_SMALL_OBJECT_SIZE_HINT'] = self.options.free_small_object_size_hint
        self._cmake.configure()

        return self._cmake

    def build(self):
        self._configure_cmake().build()

    def package(self):
        self._configure_cmake().install()
        rmdir(os.path.join(self.package_folder, "share"))
        self.copy("LICENSE*", src=self.folders.base_source, dst="licenses")
        self.copy("COPYRIGHT", src=self.folders.base_source, dst="licenses")

    def package_info(self):
        name = "Metall"
        self.cpp_info.set_property("cmake_file_name", name)
        self.cpp_info.names["cmake_find_package"] = name
        self.cpp_info.names["cmake_find_package_multi"] = name
        self.cpp_info.set_property("cmake_target_name", f"{name}::{name}")

        # TODO: to remove in conan v2 once pkg_config generators removed
        self.cpp_info.names["pkg_config"] = name

        if self.settings.os in ["Linux"]:
            self.cpp_info.system_libs = ["pthread"]

        if self.settings.compiler == "gcc" or (self.settings.os == "Linux" and self.settings.compiler == "clang"):
            if tools.Version(self.settings.compiler.version) < 9:
                self.cpp_info.system_libs += ["stdc++fs"]
