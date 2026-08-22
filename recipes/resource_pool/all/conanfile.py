import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class ResourcePool(ConanFile):
    name = "resource_pool"
    description = "C++ header only library purposed to create pool of some resources like keepalive connections"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://github.com/elsid/resource_pool"
    topics = ("resource pool", "asio", "elsid", "c++17", "cpp17", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15",
            "clang": "5",
            "apple-clang": "10",
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Only compatible with Boost up to v1.79
        self.requires("boost/1.79.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        compiler = self.settings.compiler
        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warning("resource_pool requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("resource_pool requires a compiler that supports at least C++17")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*",
             dst=os.path.join(self.package_folder, "include", "yamail"),
             src=os.path.join(self.source_folder, "include", "yamail"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        main_comp = self.cpp_info.components["_resource_pool"]
        main_comp.requires = ["boost::boost", "boost::system", "boost::thread"]
        main_comp.defines = ["BOOST_ASIO_USE_TS_EXECUTOR_AS_DEFAULT"]

        if self.settings.os == "Windows":
            main_comp.system_libs.append("ws2_32")

        # Set up for compatibility with existing cmake configuration:
        # https://github.com/elsid/resource_pool/blob/3ea1f95/examples/CMakeLists.txt#L6C34-L6C54
        self.cpp_info.set_property("cmake_target_name", "elsid::resource_pool")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "resource_pool"
        self.cpp_info.filenames["cmake_find_package_multi"] = "resource_pool"
        self.cpp_info.names["cmake_find_package"] = "elsid"
        self.cpp_info.names["cmake_find_package_multi"] = "elsid"
        main_comp.names["cmake_find_package"] = "resource_pool"
        main_comp.names["cmake_find_package_multi"] = "resource_pool"
