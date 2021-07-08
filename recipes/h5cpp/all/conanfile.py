import os

from conans import ConanFile, CMake, tools


class H5cppConan(ConanFile):
    name = "h5cpp"
    version = "0.4.1"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ess-dmsc/h5cpp"
    description = "h5cpp is a new C++ wrapper for HDF5s C-API"
    topics = ("HDF5",)
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _has_std_filesystem(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.cppstd:
            return tools.valid_min_cppstd(self, minimal_cpp_standard)

        # Information from https://en.cppreference.com/w/cpp/compiler_support
        minimal_version = {
            "gcc": "8",
            "clang": "7",
            "apple-clang": "11",
            "Visual Studio": "19.14"
        }
        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warn("%s std::filesystem support unknown. Boost will be used." % compiler)
            return False

        version = tools.Version(self.settings.compiler.version)
        return version >= minimal_version[compiler]

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("hdf5/1.12.0")
        if not self._has_std_filesystem:
            self.requires("boost/1.76.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions.update({
            "CONAN": "DISABLE",
            "WITH_BOOST": not self._has_std_filesystem,
            "BUILD_DOCS": False,
            "DISABLE_TESTS": True
        })
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
