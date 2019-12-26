import os
from conans import ConanFile, CMake, tools


class DataFrameConan(ConanFile):
    name = "DataFrame"
    license = "BSD 3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    repo_url = "https://github.com/hosseinmoein/DataFrame"
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
    exports_sources = "CMakeLists.txt"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-V-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
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
        ]:
            tools.rmdir(os.path.join(self.package_folder, dir_to_remove))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        # in linux we need to link also with these libs
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["pthread", "dl", "rt"])
