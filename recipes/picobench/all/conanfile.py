from from conan import ConanFile, tools
from conans import CMake
import functools
import os

required_conan_version = ">=1.33.0"

class PicobenchConan(ConanFile):
    name = "picobench"
    description = "A micro microbenchmarking library for C++11 in a single header file"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/iboB/picobench"
    topics = ("benchmark", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_cli": [True, False],
    }
    default_options = {
        "with_cli": False,
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def package_id(self):
        if self.options.with_cli:
            del self.info.settings.compiler
        else:
            self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PICOBENCH_BUILD_TOOLS"] = self.options.with_cli
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        if self.options.with_cli:
            binpath = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH env var: {}".format(binpath))
            self.env_info.PATH.append(binpath)

        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
