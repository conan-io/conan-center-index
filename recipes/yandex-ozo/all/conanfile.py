import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class YandexOzoConan(ConanFile):
    name = "yandex-ozo"
    description = "C++ header-only library for asynchronous access to PostgreSQL databases using ASIO"
    license = "PostgreSQL"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yandex/ozo"
    topics = ("ozo", "yandex", "postgres", "postgresql", "cpp17", "database", "db", "asio", "header-only")

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
        self.requires("boost/1.79.0")
        self.requires("resource_pool/cci.20210322")
        self.requires("libpq/15.4")

    def package_id(self):
        self.info.clear()

    def _validate_compiler_settings(self):
        compiler = self.settings.compiler
        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)

        if not minimum_version:
            self.output.warning("ozo requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("ozo requires a compiler that supports at least C++17")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("ozo does currently not support windows")

        self._validate_compiler_settings()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include", "ozo"),
             src=os.path.join(self.source_folder, "include", "ozo"))
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        main_comp = self.cpp_info.components["_ozo"]
        main_comp.requires = ["boost::boost", "boost::system", "boost::thread", "boost::coroutine", "resource_pool::resource_pool", "libpq::pq"]
        main_comp.defines = ["BOOST_HANA_CONFIG_ENABLE_STRING_UDL", "BOOST_ASIO_USE_TS_EXECUTOR_AS_DEFAULT"]
        main_comp.set_property("cmake_target_name", "yandex::ozo")

        compiler = self.settings.compiler
        version = Version(compiler.version)
        if compiler == "clang" or compiler == "apple-clang" or (compiler == "gcc" and version >= 9):
            main_comp.cxxflags = ["-Wno-gnu-string-literal-operator-template", "-Wno-gnu-zero-variadic-macro-arguments"]

        self.cpp_info.set_property("cmake_file_name", "ozo")
        self.cpp_info.set_property("cmake_target_name", "yandex::ozo")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "ozo"
        self.cpp_info.filenames["cmake_find_package_multi"] = "ozo"
        self.cpp_info.names["cmake_find_package"] = "yandex"
        self.cpp_info.names["cmake_find_package_multi"] = "yandex"
        main_comp.names["cmake_find_package"] = "ozo"
        main_comp.names["cmake_find_package_multi"] = "ozo"
