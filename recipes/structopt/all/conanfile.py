import os
from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class StructoptConan(ConanFile):
    name = "structopt"
    description = "Parse command line arguments by defining a struct+"
    topics = ("structopt", "argument-parser", "cpp17", "header-only",
        "single-header-lib", "header-library", "command-line", "arguments",
        "mit-license", "modern-cpp", "structopt", "lightweight", "reflection",
        "cross-platform", "library", "type-safety", "type-safe", "argparse",
        "clap",)
    license = "MIT"
    homepage = "https://github.com/p-ranav/structopt"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def requirements(self):
        self.requires("magic_enum/0.8.0")
        self.requires("visit_struct/1.0")

    def package_id(self):
        self.info.header_only()

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "15.0",
            "clang": "5",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, "17")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.scm.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("structopt: Unsupported compiler: {}-{} "
                                                "(https://github.com/p-ranav/structopt#compiler-compatibility)."
                                                .format(self.settings.compiler, self.settings.compiler.version))
        else:
            self.output.warn("{} requires C++14. Your compiler is unknown. Assuming it supports C++14.".format(self.name))

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        tools.files.rmdir(self, os.path.join(self._source_subfolder, "include", "structopt", "third_party"))


    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
