from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.33.0"


class UnicornConan(ConanFile):
    name = "unicorn"
    description = "Unicorn is a lightweight multi-platform, multi-architecture CPU emulator framework."
    topics = ("emulator", "security", "arm", "framework", "cpu", "mips", "x86-64", "reverse-engineering", "x86", "arm64", "sparc", "m68k")
    homepage = "https://www.unicorn-engine.org/"
    url = "https://github.com/conan-io/conan-center-index"
    license = ("GPL-2-or-later", "LGPL-2-or-later")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "supported_archs": "ANY",
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "supported_archs": "",  # defaults to all supported archs. See `config_options`.
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _all_supported_archs(self):
        """
        Get all supported architectures of the current version
        :return: sorted list of strings
        """
        return sorted(["aarch64", "arm", "m68k", "mips", "sparc", "x86"])

    @property
    def _supported_archs(self):
        """
        Get supported architectures by the current build/package
        :return: sorted list of strings
        """
        return sorted(set(str(self.options.supported_archs).split(",")))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        self.options.supported_archs = ",".join(self._all_supported_archs)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        unsupported_archs = [arch for arch in self._supported_archs if arch not in self._all_supported_archs]
        if unsupported_archs:
            self.output.info(f"Valid supported architectures are: {self._all_supported_archs}")
            raise ConanInvalidConfiguration(f"Invalid arch(s) in supported_archs option: {unsupported_archs}")

    def package_id(self):
        # normalize the supported_archs option (sorted+comma separated)
        self.info.options.supported_archs = ",".join(self._supported_archs)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["UNICORN_INSTALL"] = True
        cmake.definitions["UNICORN_BUILD_SAMPLES"] = False
        cmake.definitions["UNICORN_ARCH"] = " ".join(self._supported_archs)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        self.copy("COPYING.LGPL2", src=self._source_subfolder, dst="licenses")
        self.copy("COPYING_GLIB", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["unicorn"]
        self.cpp_info.names["pkg_config"] = "unicorn"
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["m", "pthread"]
