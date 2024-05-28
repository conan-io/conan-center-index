from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rename, replace_in_file
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"


class AsyncSimpleConan(ConanFile):
    name = "async_simple"
    description = "Simple, light-weight and easy-to-use asynchronous components"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/alibaba/async_simple"
    topics = ("modules", "asynchronous", "coroutines", "cpp20", "header-only")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "header_only": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "header_only": True
    }

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "17",
            "msvc": "193",
            "gcc": "10.3",
            "clang": "13",
            "apple-clang": "14",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.header_only:
            self.options.rm_safe("fPIC")
            self.options.rm_safe("shared")
        elif self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        if self.options.header_only:
            basic_layout(self, src_folder="src")
        else:
            cmake_layout(self, src_folder="src")

    def package_id(self):
        if self.info.options.header_only:
            self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")
        if not self.options.header_only and self.settings.os == "Windows":
            raise ConanInvalidConfiguration(f'{self.ref} cannot use uthread on Windows, and therefore it\'s only supported as a header-only library in this configuration with "{self.name}/*:header_only=True"')

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if not self.options.header_only:
            tc = CMakeToolchain(self)
            tc.cache_variables["ASYNC_SIMPLE_BUILD_DEMO_EXAMPLE"] = False
            tc.cache_variables["ASYNC_SIMPLE_ENABLE_TESTS"] = False
            tc.cache_variables["ASYNC_SIMPLE_ENABLE_ASAN"] = False
            #libaio is only used in SimpleIOExecutor which is only used in executor tests and not meant for end users
            tc.cache_variables["ASYNC_SIMPLE_DISABLE_AIO"] = True 
            tc.generate()
            
    def build(self):
        apply_conandata_patches(self)
        if not self.options.header_only:
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), '-D_GLIBCXX_USE_CXX11_ABI=1', '')
            cmake = CMake(self)
            cmake.configure()
            cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        
        if self.options.header_only:
            hCopyExcludes = ("test", "uthread", "executors")
        if not self.options.header_only:
            hCopyExcludes = ("test", "executors")
            if self.options.shared:
                if self.settings.os == "Macos":
                    sharedLibExt = "*.dylib*"
                else:
                    sharedLibExt = "*.so*"
                copy(self, pattern=sharedLibExt,
                    dst=os.path.join(self.package_folder, "lib"),
                    src=os.path.join(self.build_folder, "async_simple")
                )
            else:
                copy(self, pattern="*.a",
                    dst=os.path.join(self.package_folder, "lib"),
                    src=os.path.join(self.build_folder, "async_simple")
                )
                libTarget = os.path.join(self.package_folder, "lib", "libasync_simple.a")
                if not os.path.isfile(libTarget):
                    rename(self, os.path.join(self.package_folder, "lib", "libasync_simple_static.a"),
                        libTarget)

        copy(self, pattern="*.h",
            dst=os.path.join(self.package_folder, "include/async_simple"),
            src=os.path.join(self.source_folder, "async_simple"),
            excludes=hCopyExcludes
        )

    def package_info(self):
        if not self.options.header_only:
            self.cpp_info.libs = ["async_simple"]
        
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread"]

        self.cpp_info.set_property("cmake_file_name", "async_simple")
        if self.options.header_only:
            self.cpp_info.set_property("cmake_target_name", "async_simple::async_simple_header_only")
            
            self.cpp_info.components["_async_simple"].names["cmake_find_package"] = "async_simple_header_only"
            self.cpp_info.components["_async_simple"].names["cmake_find_package_multi"] = "async_simple_header_only"
            self.cpp_info.components["_async_simple"].set_property("cmake_target_name", "async_simple::async_simple_header_only")
        else:
            self.cpp_info.set_property("cmake_target_name", "async_simple::async_simple")
            
            self.cpp_info.components["_async_simple"].names["cmake_find_package"] = "async_simple"
            self.cpp_info.components["_async_simple"].names["cmake_find_package_multi"] = "async_simple"
            self.cpp_info.components["_async_simple"].set_property("cmake_target_name", "async_simple::async_simple")

        self.cpp_info.filenames["cmake_find_package"] = "async_simple"
        self.cpp_info.filenames["cmake_find_package_multi"] = "async_simple"
        self.cpp_info.names["cmake_find_package"] = "async_simple"
        self.cpp_info.names["cmake_find_package_multi"] = "async_simple"
