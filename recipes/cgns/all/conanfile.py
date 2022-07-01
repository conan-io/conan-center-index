import os
from conans import ConanFile, CMake, tools


required_conan_version = ">=1.33.0"


class CgnsConan(ConanFile):
    name = "cgns"
    description = "Standard for data associated with the numerical solution " \
                  "of fluid dynamics equations."
    topics = ("cgns", "data", "cfd", "fluids")
    homepage = "http://cgns.org/"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake", "cmake_find_package"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_hdf5": [True, False],
        "parallel": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_hdf5": True,
        "parallel": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.options.parallel and not self.options.with_hdf5:
            raise ConanInvalidConfiguration("Parallel requires HDF5 with parallel enabled")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.options.parallel:
            self.options["hdf5"].parallel = True
            self.options["hdf5"].enable_cxx = False # can't enable this with parallel

    def requirements(self):
        if self.options.with_hdf5:
            self.requires("hdf5/1.12.2")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                strip_root=True,
                destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["CGNS_ENABLE_TESTS"] = False
        self._cmake.definitions["CGNS_BUILD_TESTING"] = False
        self._cmake.definitions["CGNS_ENABLE_FORTRAN"] = False
        self._cmake.definitions["CGNS_ENABLE_HDF5"] = self.options.with_hdf5
        self._cmake.definitions["CGNS_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["CGNS_USE_SHARED"] = self.options.shared
        self._cmake.definitions["CGNS_ENABLE_PARALLEL"] = self.options.parallel
        self._cmake.definitions["CGNS_BUILD_CGNSTOOLS"] = False
        self._cmake.configure()

        # Other flags, seen in appveyor.yml in source code, not currently managed.
        # CGNS_ENABLE_LFS:BOOL=OFF       --- note in code: needed on 32 bit systems
        # CGNS_ENABLE_SCOPING:BOOL=OFF   --- disabled in VTK's bundle
        # HDF5_NEED_ZLIB:BOOL=ON -- should be dealt with by cmake auto dependency management or something?

        return self._cmake

    def build(self):
        # conan complains about CRLF in this file, so fix it up
        tools.dos2unix(os.path.join(self.source_folder,self._source_subfolder,"src","cgnstools","common", "winhtml.c"))

        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build(target="cgns_shared" if self.options.shared else "cgns_static")

    def package(self):
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        os.remove(os.path.join(self.package_folder, "include", "cgnsBuild.defs"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["cgnsdll" if self.settings.os == "Windows" and self.options.shared else "cgns"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines = ["CGNSDLL=__declspec(dllimport)"] # we could instead define USE_DLL but it's too generic
