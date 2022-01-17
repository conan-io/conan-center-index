import functools
import os

from conans import CMake, ConanFile, tools

required_conan_version = ">=1.43.0"


class CloopConan(ConanFile):
    name = "asfernandes-cloop"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/asfernandes/cloop"
    description = "Cross Language Object Oriented Programming"
    topics = ("parser", "idl")
    license = "???"
    settings = ("os", "arch", "compiler", "build_type")
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    generators = ("cmake",)
    # FIXME: remove the CML once https://github.com/asfernandes/cloop/pull/7 is
    #        merged
    exports_sources = ("CMakeLists.txt", "idpl.txt")
    no_copy_source = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        self._configure_cmake().build()

    def package(self):
        self.copy("idpl.txt", "licenses")
        self._configure_cmake().install()

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
