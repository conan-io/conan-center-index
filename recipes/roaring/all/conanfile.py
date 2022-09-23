from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import functools

required_conan_version = ">=1.43.0"

class RoaringConan(ConanFile):
    name = "roaring"
    description = "Portable Roaring bitmaps in C and C++"
    license = ("Apache-2.0", "MIT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/RoaringBitmap/CRoaring"
    topics = ("bitset", "compression", "index", "format")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_avx": [True, False],
        "with_neon": [True, False],
        "native_optimization": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_avx": True,
        "with_neon": True,
        "native_optimization": False,
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
          return "source_subfolder"

    @property
    def _build_subfolder(self):
          return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ("x86", "x86_64"):
            del self.options.with_avx
        if not str(self.settings.arch).startswith("arm"):
            del self.options.with_neon

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "11")
        if tools.Version(self.version) >= "0.3.0":
            if self.settings.compiler == "apple-clang" and tools.Version(self.settings.compiler.version) < "11":
                raise ConanInvalidConfiguration("roaring >= 3.0.0 requires at least apple-clang 11 to support runtime dispatching.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ROARING_DISABLE_AVX"] = not self.options.get_safe("with_avx", False)
        cmake.definitions["ROARING_DISABLE_NEON"] = not self.options.get_safe("with_neon", False)
        cmake.definitions["ROARING_DISABLE_NATIVE"] = not self.options.native_optimization
        cmake.definitions["ROARING_BUILD_STATIC"] = not self.options.shared
        cmake.definitions["ENABLE_ROARING_TESTS"] = False
        # Relocatable shared lib on Macos
        cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "set(CMAKE_MACOSX_RPATH OFF)", "")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs = ["roaring"]

        self.cpp_info.set_property("cmake_target_name", "roaring::roaring")
        self.cpp_info.set_property("pkg_config_name", "roaring")

        self.cpp_info.names["cmake_find_package"] = "roaring"
        self.cpp_info.names["cmake_find_package_multi"] = "roaring"
        self.cpp_info.names["pkg_config"] = "roaring"
