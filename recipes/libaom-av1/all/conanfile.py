from conans import ConanFile, tools, CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.36.0"


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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.arch not in ("x86", "x86_64"):
            del self.options.assembly

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if self.options.get_safe("assembly", False):
            self.build_requires("nasm/2.15.05")
        if self._settings_build.os == "Windows":
            self.build_requires("strawberryperl/5.30.0.1")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
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
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder,
                  strip_root=tools.Version(self.version) >= "3.3.0")

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["ENABLE_EXAMPLES"] = False
        cmake.definitions["ENABLE_TESTS"] = False
        cmake.definitions["ENABLE_DOCS"] = False
        cmake.definitions["ENABLE_TOOLS"] = False
        if not self.options.get_safe("assembly", False):
            # make non-assembly build
            cmake.definitions["AOM_TARGET_CPU"] = "generic"
        # libyuv is used for examples, tests and non-essential 'dump_obu' tool so it is disabled
        # required to be 1/0 instead of False
        cmake.definitions["CONFIG_LIBYUV"] = 0
        # webm is not yet packaged
        cmake.definitions["CONFIG_WEBM_IO"] = 0
        # required out-of-source build
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "aom")
        self.cpp_info.libs = ["aom"]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "m"]

        self.cpp_info.names["pkg_config"] = "aom"
