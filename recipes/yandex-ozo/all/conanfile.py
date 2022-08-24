from conan import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
from conans.tools import check_min_cppstd, Version
import os

required_conan_version = ">=1.33.0"


class YandexOzoConan(ConanFile):
    name = "yandex-ozo"
    description = "C++ header-only library for asynchronous access to PostgreSQL databases using ASIO"
    topics = ("ozo", "yandex", "postgres", "postgresql", "cpp17", "database", "db", "asio")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yandex/ozo"
    license = "PostgreSQL"

    settings = "os", "compiler"
    requires = ("boost/1.76.0", "resource_pool/cci.20210322", "libpq/13.2")
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15",
            "clang": "5",
            "apple-clang": "10",
        }

    def _validate_compiler_settings(self):
        compiler = self.settings.compiler
        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, "17")
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)

        if not minimum_version:
            self.output.warn("ozo requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif tools.scm.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("ozo requires a compiler that supports at least C++17")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("ozo does currently not support windows")

        self._validate_compiler_settings()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="*", dst=os.path.join("include", "ozo"), src=os.path.join(self._source_subfolder, "include", "ozo"))
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        main_comp = self.cpp_info.components["_ozo"]
        main_comp.requires = [
            "boost::boost", "boost::system", "boost::thread", "boost::coroutine",
            "resource_pool::resource_pool",
            "libpq::pq",
        ]
        main_comp.defines = [
            "BOOST_HANA_CONFIG_ENABLE_STRING_UDL",
            "BOOST_ASIO_USE_TS_EXECUTOR_AS_DEFAULT",
        ]
        main_comp.names["cmake_find_package"] = "ozo"
        main_comp.names["cmake_find_package_multi"] = "ozo"

        compiler = self.settings.compiler
        version = Version(compiler.version)
        if compiler == "clang" or compiler == "apple-clang" or (compiler == "gcc" and version >= 9):
            main_comp.cxxflags = [
                "-Wno-gnu-string-literal-operator-template",
                "-Wno-gnu-zero-variadic-macro-arguments",
            ]

        self.cpp_info.filenames["cmake_find_package"] = "ozo"
        self.cpp_info.filenames["cmake_find_package_multi"] = "ozo"
        self.cpp_info.names["cmake_find_package"] = "yandex"
        self.cpp_info.names["cmake_find_package_multi"] = "yandex"
