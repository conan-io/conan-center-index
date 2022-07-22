import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir, apply_conandata_patches


required_conan_version = ">=1.43.0"


class CgnsConan(ConanFile):
    name = "cgns"
    description = "Standard for data associated with the numerical solution " \
                  "of fluid dynamics equations."
    topics = ("cgns", "data", "cfd", "fluids")
    homepage = "http://cgns.org/"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
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

    def export_sources(self):
        copy(self, "CMakeLists.txt", src=".", dst=self.export_sources_folder)
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, patch["patch_file"], src=".", dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def validate(self):
        if self.info.options.parallel and not (self.info.options.with_hdf5 and self.info.options["hdf5"].parallel):
            raise ConanInvalidConfiguration("The option 'parallel' requires HDF5 with parallel=True")
        if self.info.options.parallel and self.info.options.with_hdf5 and self.info.options["hdf5"].enable_cxx:
            raise ConanInvalidConfiguration("The option 'parallel' requires HDF5 with enable_cxx=False")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            # In windows, with msvc, the compiler.libcxx doesn't exist, so it will raise.
            del self.settings.compiler.libcxx
        except Exception:
            pass
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_hdf5:
            self.requires("hdf5/1.13.1")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CGNS_ENABLE_TESTS"] = False
        tc.variables["CGNS_BUILD_TESTING"] = False
        tc.variables["CGNS_ENABLE_FORTRAN"] = False
        tc.variables["CGNS_ENABLE_HDF5"] = self.options.with_hdf5
        tc.variables["CGNS_BUILD_SHARED"] = self.options.shared
        tc.variables["CGNS_USE_SHARED"] = self.options.shared
        tc.variables["CGNS_ENABLE_PARALLEL"] = self.options.parallel
        tc.variables["CGNS_BUILD_CGNSTOOLS"] = False
        # CMAKE_BUILD_TYPE is not set by all the CMake generators, but cgns needs it
        tc.variables["CMAKE_BUILD_TYPE"] = self.settings.build_type
        tc.generate()

        # Other flags, seen in appveyor.yml in source code, not currently managed.
        # CGNS_ENABLE_LFS:BOOL=OFF       --- note in code: needed on 32 bit systems
        # CGNS_ENABLE_SCOPING:BOOL=OFF   --- disabled in VTK's bundle
        # HDF5_NEED_ZLIB:BOOL=ON -- should be dealt with by cmake auto dependency management or something?

    def build(self):
        apply_conandata_patches(self)

        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="cgns_shared" if self.options.shared else "cgns_static")

    def package(self):
        copy(self, "license.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

        cmake = CMake(self)
        cmake.install()

        os.remove(os.path.join(self.package_folder, "include", "cgnsBuild.defs"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "CGNS")
        self.cpp_info.set_property("cmake_target_name", "CGNS::CGNS")

        if self.options.shared:
            self.cpp_info.components["cgns_shared"].set_property("cmake_target_name", "CGNS::cgns_shared")
            self.cpp_info.components["cgns_shared"].libs = ["cgnsdll" if self.settings.os == "Windows" else "cgns"]
            if self.options.with_hdf5:
                self.cpp_info.components["cgns_shared"].requires = ["hdf5::hdf5"]
            if self.settings.os == "Windows":
                # we could instead define USE_DLL but it's too generic
                self.cpp_info.components["cgns_shared"].defines = ["CGNSDLL=__declspec(dllimport)"]
        else:
            self.cpp_info.components["cgns_static"].set_property("cmake_target_name", "CGNS::cgns_static")
            self.cpp_info.components["cgns_static"].libs = ["cgns"]
            if self.options.with_hdf5:
                self.cpp_info.components["cgns_static"].requires = ["hdf5::hdf5"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "CGNS"
        self.cpp_info.names["cmake_find_package_multi"] = "CGNS"
