import functools
import os

from conans import CMake, ConanFile, tools

required_conan_version = ">=1.43.0"


class BisonConan(ConanFile):
    name = "btyacc"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ChrisDodd/btyacc"
    description = "Backtracking yacc"
    topics = ("yacc", "parser")
    license = "???"
    settings = ("os", "arch", "compiler", "build_type")
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }
    generators = ("cmake",)
    # FIXME: remove these once https://github.com/ChrisDodd/btyacc/pull/27 is
    #        merged and enable no_copy_source
    exports_sources = ("patches/*", "CMakeLists.txt", "cmake/*.cmake")
    # no_copy_source = True

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        self._configure_cmake().build()

    def package(self):
        self.copy("README", "licenses")
        self.copy("README.BYACC", "licenses")
        self._configure_cmake().install()

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bindir}")
        self.env_info.PATH.append(bindir)
