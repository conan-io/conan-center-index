from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.33.0"


class ConanRecipe(ConanFile):
    name = "roaring"

    description = "Portable Roaring bitmaps in C and C++"
    topics = ("conan", "bitset", "compression", "index", "format")

    homepage = "https://github.com/RoaringBitmap/CRoaring"
    url = "https://github.com/conan-io/conan-center-index"
    license = "Apache-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "avx": [True, False],
        "neon": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "avx": True,
        "neon": True,
    }

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
          return "source_subfolder"

    @property
    def _build_subfolder(self):
          return "build_subfolder"

    @property
    def _has_axv_support(self):
          return self.settings.arch in ["x86", "x86_64"]

    @property
    def _has_neon_support(self):
          return "arm" in self.settings.arch

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_axv_support:
            del self.options.avx
        if not self._has_neon_support:
            del self.options.neon

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ROARING_DISABLE_X64"] = not self.settings.arch in ["x86", "x86_64"]
        self._cmake.definitions["ROARING_DISABLE_AVX"] = not self.options.get_safe("avx", False)
        self._cmake.definitions["ROARING_DISABLE_NEON"] = not self.options.get_safe("neon", False)
        self._cmake.definitions["ROARING_DISABLE_NATIVE"] = True
        self._cmake.definitions["ROARING_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["ENABLE_ROARING_TESTS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "roaring"
        self.cpp_info.names["cmake_find_package_multi"] = "roaring"
        self.cpp_info.libs = ["roaring"]
