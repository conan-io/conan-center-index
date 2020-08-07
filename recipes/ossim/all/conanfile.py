from conans import CMake, ConanFile, tools
import os


class OssimConan(ConanFile):
    name = "ossim"
    description = "OSSIM is a geospatial image processing library used by government, commercial, educational, and private entities throughout the solar system."
    topics = ("conan", "ossim")
    license = "MIT"
    homepage = "https://github.com/ossimlabs/ossim"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "CMakeLists.txt", "patches/**"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_freetype": [True, False],
        "with_hdf5": [True, False],
        "with_mpi": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_freetype": True,
        "with_hdf5": True,
        "with_mpi": False,
    }
    generators = "cmake", "cmake_find_package"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("geos/3.8.1")
        self.requires("jsoncpp/1.9.3")
        self.requires("libgeotiff/1.6.0")
        self.requires("libtiff/4.1.0")
        self.requires("libjpeg/9d")
        self.requires("zlib/1.2.11")
        if self.options.with_freetype:
            self.requires("freetype/2.10.2")
        if self.options.with_hdf5:
            self.requires("hdf5/1.12.0")
        if self.options.with_mpi:
            self.requires("mpi/3.0.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_OSSIM_FREETYPE_SUPPORT"] = self.options.with_freetype
        self._cmake.definitions["BUILD_OSSIM_HDF5_SUPPORT"] = self.options.with_hdf5
        self._cmake.definitions["BUILD_OSSIM_MPI_SUPPORT"] = self.options.with_mpi
        self._cmake.definitions["BUILD_OSSIM_CURL_APPS"] = False
        self._cmake.definitions["BUILD_OSSIM_ID_SUPPORT"] = False
        self._cmake.definitions["BUILD_OSSIM_APPS"] = False
        self._cmake.definitions["BUILD_OSSIM_CURL_APPS"] = False
        self._cmake.definitions["BUILD_OSSIM_TESTS"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(os.path.join(self._source_subfolder, "cmake", "CMakeModules")):
            for file in os.listdir("."):
                name, ext = os.path.splitext(file)
                if name.lower() in ("findgit", ):
                    continue
                if file.startswith("Find") and ext.lower() == ".cmake":
                    os.unlink(file)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.mkdir(os.path.join(self.package_folder, "bin"))
        os.rename(os.path.join(self.package_folder, "share"),
                  os.path.join(self.package_folder, "bin", "share"))

    def package_info(self):
        self.cpp_info.libs = ["ossim"]
