from os import path
from conan import ConanFile
from conan.tools.microsoft import is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout


required_conan_version = ">=1.53.0"

class METISConan(ConanFile):
    name = "metis"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/KarypisLab/METIS"
    description = "set of serial programs for partitioning graphs," \
                  " partitioning finite element meshes, and producing" \
                  " fill reducing orderings for sparse matrices"
    topics = ("karypislab", "graph", "partitioning-algorithms")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_64bit_types": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_64bit_types": True,
    }

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("gklib/5.1.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        tc.variables["SHARED"] = self.options.shared
        tc.variables["METIS_INSTALL"] = True
        tc.variables["ASSERT"] = self.settings.build_type == "Debug"
        tc.variables["ASSERT2"] = self.settings.build_type == "Debug"
        tc.variables["METIS_IDX64"] = self.with_64bit_types
        tc.variables["METIS_REAL64"] = self.with_64bit_types
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.variables["GKLIB_PATH"] = path.join(self.source_folder, "GKlib")
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["metis"]
        self.cpp_info.requires.append("gklib::gklib")

        self.cpp_info.set_property("cmake_file_name", "metis")
        self.cpp_info.set_property("cmake_target_name", "metis::metis")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        if is_msvc(self) or self._is_mingw:
            self.cpp_info.defines.append("USE_GKREGEX")
        if is_msvc(self):
            self.cpp_info.defines.append("__thread=__declspec(thread)")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "METIS"
        self.cpp_info.filenames["cmake_find_package_multi"] = "metis"
        self.cpp_info.names["cmake_find_package"] = "METIS"
        self.cpp_info.names["cmake_find_package_multi"] = "metis"
