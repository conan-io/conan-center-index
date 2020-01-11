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
        v = "V-{}".format(self.version) if self.version == "1.5.0" else self.version
        extracted_folder = "DataFrame-{}".format(v)
        os.rename(extracted_folder, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        # DataFrame v1.5.0 requires C++14, while v1.6.0 C++17 is required.
        version = tools.Version(self.settings.compiler.version)
        compiler = self.settings.compiler
        if (
            compiler == "Visual Studio"
            and Version(self.settings.compiler.version) < "15"
        ):
            raise ConanInvalidConfiguration("DataFrame requires Visual Studio >= 15")
        if (
            (compiler == "gcc" and version < "7")
            or (compiler == "clang" and version < "6")
            or (compiler == "apple-clang" and version < "9")
        ):
            raise ConanInvalidConfiguration("DataFrame v1.6.0 requires at least C++17")

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
