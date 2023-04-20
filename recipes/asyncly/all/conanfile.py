from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"

class PackageConan(ConanFile):
    name = "asyncly"
    description = "High level concurrency primitives for C++"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/goto-opensource/asyncly"
    topics = ("c++", "asynchronous", "communication")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "clang": "13",
            "apple-clang": "13",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.81.0", transitive_headers=True)
        self.requires("function2/4.2.2", transitive_headers=True)
        self.requires("prometheus-cpp/1.1.0", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 192)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_TESTING"] = False
        if is_msvc(self):
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["asyncly"]
        self.cpp_info.requires = ["boost::headers", "function2::function2", "prometheus-cpp::prometheus-cpp-core"]

        self.cpp_info.set_property("cmake_file_name", "asyncly")
        self.cpp_info.set_property("cmake_target_name", "asyncly::asyncly")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "asyncly"
        self.cpp_info.filenames["cmake_find_package_multi"] = "asyncly"
        self.cpp_info.names["cmake_find_package"] = "asyncly"
        self.cpp_info.names["cmake_find_package_multi"] = "asyncly"
