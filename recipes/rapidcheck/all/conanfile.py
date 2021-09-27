from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class RapidcheckConan(ConanFile):
    name = "rapidcheck"
    description = "QuickCheck clone for C++ with the goal of being simple to use with as little boilerplate as possible"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/emil-e/rapidcheck"
    license = "BSD-2-Clause"
    topics = "quickcheck", "testing", "property-testing"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = ["cmake", "cmake_find_package"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_rtti": [True, False],
        "enable_catch": [True, False],
        "enable_gmock": [True, False],
        "enable_gtest": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_rtti": True,
        "enable_catch": False,
        "enable_gmock": False,
        "enable_gtest": False
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("shared is not supported using Visual Studio")

    def requirements(self):
        if self.options.enable_catch:
            self.requires("catch2/2.13.7")
        if self.options.enable_gmock or self.options.enable_gtest:
            self.requires("gtest/1.11.0")
            
    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["RC_ENABLE_RTTI"] = self.options.enable_rtti
        self._cmake.definitions["RC_ENABLE_TESTS"] = False
        self._cmake.definitions["RC_ENABLE_EXAMPLES"] = False
        self._cmake.definitions["RC_ENABLE_CATCH"] = self.options.enable_catch
        self._cmake.definitions["RC_ENABLE_GMOCK"] = self.options.enable_gmock
        self._cmake.definitions["RC_ENABLE_GTEST"] = self.options.enable_gtest
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        if self.options.enable_gmock and not self.deps_cpp_info["gtest"].build_gmock:
            raise ConanInvalidConfiguration("The option `rapidcheck:enable_gmock` requires gtest:build_gmock=True`")
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE*", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"rapidcheck": "rapidcheck::rapidcheck", 
             "rapidcheck_catch":"rapidcheck::rapidcheck_catch", 
             "rapidcheck_gmock": "rapidcheck::rapidcheck_gmock", 
             "rapidcheck_gtest": "rapidcheck::rapidcheck_gtest"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "rapidcheck"
        self.cpp_info.names["cmake_find_package_multi"] = "rapidcheck"
        
        self.cpp_info.components["rapidcheck_rapidcheck"].set_property("cmake_target_name", "rapidcheck")
        self.cpp_info.components["rapidcheck_rapidcheck"].builddirs.append(self._module_subfolder)
        self.cpp_info.components["rapidcheck_rapidcheck"].set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.components["rapidcheck_rapidcheck"].libs = ["rapidcheck"]
        version = self.version[4:]
        if tools.Version(version) < "20201218":
            if self.options.enable_rtti:
                self.cpp_info.components["rapidcheck_rapidcheck"].defines.append("RC_USE_RTTI")
        else:
            if not self.options.enable_rtti:
                self.cpp_info.components["rapidcheck_rapidcheck"].defines.append("RC_DONT_USE_RTTI")
                
        if self.options.enable_catch:
            self.cpp_info.components["rapidcheck_catch"].requires = ["rapidcheck_rapidcheck", "catch2::catch2"]
        if self.options.enable_gmock:
            self.cpp_info.components["rapidcheck_gmock"].requires = ["rapidcheck_rapidcheck", "gtest::gtest"]
        if self.options.enable_gtest:
            self.cpp_info.components["rapidcheck_gtest"].requires = ["rapidcheck_rapidcheck", "gtest::gtest"]
        
