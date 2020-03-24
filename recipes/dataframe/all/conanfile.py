import os
from conans import ConanFile, CMake, tools
from conans.tools import Version
from conans.errors import ConanInvalidConfiguration


class DataFrameConan(ConanFile):
    name = "dataframe"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hosseinmoein/DataFrame"
    description = "C++ DataFrame -- R's and Pandas DataFrame in modern C++ using native types, continuous memory storage, and no virtual functions"
    topics = (
        "conan",
        "dataframe",
        "numerical-analysis",
        "multidimensional-data",
        "heterogeneous",
    )
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/*"]

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "source_subfolder")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "DataFrame-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        compiler = str(self.settings.compiler)
        compiler_version = tools.Version(self.settings.compiler.version)

        if compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration(
                "Could not support this specific configuration. Try static."
            )

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "17")
        else:
            self.output.warn(
                "{} recipe lacks information about the {} compiler standard version support".format(
                    self.name, compiler
                )
            )

        minimal_version = {
            "Visual Studio": "15",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "9.0",
        }

        if compiler not in minimal_version:
            self.output.info(
                "{} requires a compiler that supports at least C++17".format(self.name)
            )
            return

        # Exclude compilers not supported by cpp-taskflow
        if compiler_version < minimal_version[compiler]:
            raise ConanInvalidConfiguration(
                "{} requires a compiler that supports at least C++17. {} {} is not supported.".format(
                    self.name, compiler, Version(self.settings.compiler.version.value)
                )
            )

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("License", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        # Remove packaging files & MS runtime files
        for dir_to_remove in [
            os.path.join("lib", "cmake"),
            os.path.join("lib", "share"),
            os.path.join("lib", "pkgconfig"),
            "CMake",
        ]:
            tools.rmdir(os.path.join(self.package_folder, dir_to_remove))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        # in linux we need to link also with these libs
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["pthread", "dl", "rt"])
