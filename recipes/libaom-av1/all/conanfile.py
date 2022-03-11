from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


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

    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/*"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.arch not in ("x86", "x86_64"):
            del self.options.assembly

    def build_requirements(self):
        if self.options.get_safe("assembly", False):
            self.build_requires("nasm/2.15.05")
        if self._settings_build.os == "Windows":
            self.build_requires("strawberryperl/5.30.0.1")

    def validate(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        # Check compiler version
        compiler = str(self.settings.compiler)
        compiler_version = tools.Version(self.settings.compiler.version.value)

        minimal_version = {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "6"
        }
        if compiler not in minimal_version:
            self.output.warn(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
        elif compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("{} requires a {} version >= {}".format(self.name, compiler, compiler_version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_EXAMPLES"] = False
        self._cmake.definitions["ENABLE_TESTS"] = False
        self._cmake.definitions["ENABLE_DOCS"] = False
        self._cmake.definitions["ENABLE_TOOLS"] = False
        if not self.options.get_safe("assembly", False):
            # make non-assembly build
            self._cmake.definitions["AOM_TARGET_CPU"] = "generic"
        # libyuv is used for examples, tests and non-essential 'dump_obu' tool so it is disabled
        # required to be 1/0 instead of False
        self._cmake.definitions["CONFIG_LIBYUV"] = 0
        # webm is not yet packaged
        self._cmake.definitions["CONFIG_WEBM_IO"] = 0
        # required out-of-source build
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.a")

    def package_info(self):
        self.cpp_info.libs = ["aom"]
        self.cpp_info.names["cmake_find_package"] = "aom"
        self.cpp_info.names["cmake_find_package_multi"] = "aom"
        self.cpp_info.names["pkg_config"] = "libaom"
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "m"]
