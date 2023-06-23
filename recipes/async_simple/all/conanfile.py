from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
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
    topics = ("modules", "asynchronous", "coroutines", "cpp20")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 20

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "10.3",
            "clang": "13",
            "apple-clang": "14",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        pass

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )
        else:
            raise ConanInvalidConfiguration("msvc not supported now")

    def build_requirements(self):
        pass

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include/async_simple"),
            src=os.path.join(self.source_folder, "async_simple"),
            excludes=("test", "executors", "uthread")
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        self.cpp_info.set_property("cmake_file_name", "async_simple")
        self.cpp_info.set_property("cmake_target_name", "async_simple::async_simple")

        self.cpp_info.filenames["cmake_find_package"] = "async_simple"
        self.cpp_info.filenames["cmake_find_package_multi"] = "async_simple"
        self.cpp_info.names["cmake_find_package"] = "async_simple"
        self.cpp_info.names["cmake_find_package_multi"] = "async_simple"
        self.cpp_info.components["_async_simple"].names["cmake_find_package"] = "async_simple_header_only"
        self.cpp_info.components["_async_simple"].names["cmake_find_package_multi"] = "async_simple_header_only"
        self.cpp_info.components["_async_simple"].set_property("cmake_target_name", "async_simple::async_simple_header_only")
