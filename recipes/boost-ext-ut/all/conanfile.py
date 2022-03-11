import os
from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.43.0"


class UTConan(ConanFile):
    name = "boost-ext-ut"
    description = ("C++20 single header/single module, "
                   "macro-free micro Unit Testing Framework")
    topics = ("ut", "header-only", "unit-test", "test", "tdd", "bdd")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://boost-ext.github.io/ut/"
    license = "BSL-1.0"
    settings = "os", "compiler", "arch", "build_type"
    no_copy_source = True
    options = { "disable_module": [True, False], }
    default_options = { "disable_module": False, }
    _cmake = None

    @property
    def _minimum_cpp_standard(self):
        return 17 if self.settings.compiler in ["clang", "gcc"] and tools.Version(self.version) <= "1.1.8" else 20

    @property
    def _minimum_compilers_version(self):
        return {
            "apple-clang": "11" if tools.Version(self.version) < "1.1.8" else "12",
            "clang": "9",
            "gcc": "9",
            "msvc": "19",
            "Visual Studio": "16",
        }

    def config_options(self):
        if tools.Version(self.version) <= "1.1.8":
            del self.options.disable_module

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} "
                             "compiler support.".format(
                                 self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    "{} requires C++{} support. "
                    "The current compiler {} {} does not support it.".format(
                        self.name, self._minimum_cpp_standard,
                        self.settings.compiler,
                        self.settings.compiler.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)
        if tools.Version(self.version) <= "1.1.8":
            tools.download("https://www.boost.org/LICENSE_1_0.txt", "LICENSE",
                       sha256="c9bff75738922193e67fa726fa225535870d2aa1059f914"
                       "52c411736284ad566")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BOOST_UT_BUILD_BENCHMARKS"] = False
        self._cmake.definitions["BOOST_UT_BUILD_EXAMPLES"] = False
        self._cmake.definitions["BOOST_UT_BUILD_TESTS"] = False
        self._cmake.definitions["PROJECT_DISABLE_VERSION_SUFFIX"] = True
        if self.options.get_safe("disable_module"):
            self._cmake.definitions["BOOST_UT_DISABLE_MODULE"] = self.options.disable_module
        self._cmake.configure()
        return self._cmake
    
    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE" if tools.Version(self.version) <= "1.1.8" else "LICENSE.md", dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ut")
        self.cpp_info.set_property("cmake_target_name", "boost::ut")

        self.cpp_info.names["cmake_find_package"] = "boost"
        self.cpp_info.names["cmake_find_package_multi"] = "boost"
        self.cpp_info.filenames["cmake_find_package"] = "ut"
        self.cpp_info.filenames["cmake_find_package_multi"] = "ut"
        self.cpp_info.components["ut"].names["cmake_find_package"] = "ut"
        self.cpp_info.components["ut"].names["cmake_find_package_multi"] = "ut"

        if self.options.get_safe("disable_module"):
            self.cpp_info.components["ut"].defines = ["BOOST_UT_DISABLE_MODULE"]

        if tools.Version(self.version) > "1.1.8":
            include_path_version = self.version
            # There was a typo in the project version number in version 1.1.9.
            if tools.Version(self.version) == "1.1.9":
                include_path_version = "1.1.8"
            self.cpp_info.components["ut"].includedirs = [os.path.join("include", "ut-" + include_path_version, "include")]
