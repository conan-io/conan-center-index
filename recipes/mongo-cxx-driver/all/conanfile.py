from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, valid_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import export_conandata_patches, apply_conandata_patches, copy, get, rm, rmdir
from conan.tools.scm import Version
import os
import shutil

required_conan_version = ">=1.54.0"


class MongoCxxConan(ConanFile):
    name = "mongo-cxx-driver"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mongocxx.org"
    description = "C++ Driver for MongoDB"
    topics = ("libbsoncxx", "libmongocxx", "mongo", "mongodb", "database", "db")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "polyfill": ["std", "boost", "mnmlstc", "experimental"],
        "with_ssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "polyfill": "boost",
        "with_ssl": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("mongo-c-driver/1.24.3")
        if self.options.polyfill == "boost":
            self.requires("boost/1.82.0", transitive_headers=True)

    @property
    def _minimal_std_version(self):
        return {
            "std": "17",
            "experimental": "14",
            "boost": "11",
            "polyfill": "11"
        }[str(self.options.polyfill)]

    @property
    def _compilers_minimum_version(self):
        if self.info.options.polyfill == "std":
            # C++17
            return {
                "Visual Studio": "15",
                "gcc": "7",
                "clang": "5",
                "apple-clang": "10"
            }
        elif self.info.options.polyfill == "experimental":
            # C++14
            return {
                "Visual Studio": "15",
                "gcc": "5",
                "clang": "3.5",
                "apple-clang": "10"
            }
        elif self.info.options.polyfill == "boost":
            # C++11
            return {
                "Visual Studio": "14",
                "gcc": "5",
                "clang": "3.3",
                "apple-clang": "9"
            }
        else:
            raise ConanException(
                f"please, specify _compilers_minimum_version for {self.options.polyfill} polyfill"
            )

    def validate(self):
        if self.options.with_ssl and not bool(self.dependencies["mongo-c-driver"].options.with_ssl):
            raise ConanInvalidConfiguration("mongo-cxx-driver with_ssl=True requires mongo-c-driver with a ssl implementation")

        if self.options.polyfill == "mnmlstc":
            # TODO: add mnmlstc polyfill support
            # Cannot model mnmlstc (not packaged, is pulled dynamically) polyfill dependencies
            raise ConanInvalidConfiguration("mnmlstc polyfill is not yet supported")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimal_std_version)

        compiler = str(self.settings.compiler)
        if self.options.polyfill == "experimental" and compiler == "apple-clang":
            raise ConanInvalidConfiguration("experimental polyfill is not supported for apple-clang")

        version = Version(self.settings.compiler.version)
        if compiler in self._compilers_minimum_version and version < self._compilers_minimum_version[compiler]:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires a compiler that supports at least C++{self._minimal_std_version}",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BSONCXX_POLY_USE_MNMLSTC"] = self.options.polyfill == "mnmlstc"
        tc.variables["BSONCXX_POLY_USE_STD"] = self.options.polyfill == "std"
        tc.variables["BSONCXX_POLY_USE_STD_EXPERIMENTAL"] = self.options.polyfill == "experimental"
        tc.variables["BSONCXX_POLY_USE_BOOST"] = self.options.polyfill == "boost"
        tc.cache_variables["BUILD_VERSION"] = self.version
        tc.cache_variables["BSONCXX_LINK_WITH_STATIC_MONGOC"] = "OFF" if self.dependencies["mongo-c-driver"].options.shared else "ON"
        tc.cache_variables["MONGOCXX_LINK_WITH_STATIC_MONGOC"] = "OFF" if self.dependencies["mongo-c-driver"].options.shared else "ON"
        tc.variables["MONGOCXX_ENABLE_SSL"] = self.options.with_ssl
        if not valid_min_cppstd(self, self._minimal_std_version):
            tc.variables["CMAKE_CXX_STANDARD"] = self._minimal_std_version
        tc.variables["ENABLE_TESTS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()
        # FIXME: two CMake module/config files should be generated (mongoc-1.0-config.cmake and bson-1.0-config.cmake),
        # but it can't be modeled right now.
        # Fix should happen in mongo-c-driver recipe
        mongoc_config_file = os.path.join(self.generators_folder, "mongoc-1.0-config.cmake")
        bson_config_file = os.path.join(self.generators_folder, "bson-1.0-config.cmake")
        if not os.path.exists(bson_config_file):
            self.output.info("Copying mongoc config file to bson")
            shutil.copy(src=mongoc_config_file, dst=bson_config_file)

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "THIRD-PARTY-NOTICES", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if self.settings.os == "Windows":
            for vc_file in ("concrt", "msvcp", "vcruntime"):
                rm(self, f"{vc_file}*.dll", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # FIXME: two CMake module/config files should be generated (mongocxx-config.cmake and bsoncxx-config.cmake),
        # but it can't be modeled right now.
        mongocxx_target = "mongocxx_shared" if self.options.shared else "mongocxx_static"
        self.cpp_info.set_property("cmake_file_name", "mongocxx")
        self.cpp_info.set_property("cmake_target_name", f"mongo::{mongocxx_target}")

        self.cpp_info.filenames["cmake_find_package"] = "mongocxx"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mongocxx"
        self.cpp_info.names["cmake_find_package"] = "mongo"
        self.cpp_info.names["cmake_find_package_multi"] = "mongo"

        # mongocxx
        self.cpp_info.components["mongocxx"].set_property("cmake_target_name", f"mongo::{mongocxx_target}")
        self.cpp_info.components["mongocxx"].set_property("pkg_config_name", "libmongocxx" if self.options.shared else "libmongocxx-static")

        self.cpp_info.components["mongocxx"].names["cmake_find_package"] = mongocxx_target
        self.cpp_info.components["mongocxx"].names["cmake_find_package_multi"] = mongocxx_target

        self.cpp_info.components["mongocxx"].libs = ["mongocxx" if self.options.shared else "mongocxx-static"]
        if not self.options.shared:
            self.cpp_info.components["mongocxx"].defines.append("MONGOCXX_STATIC")
        self.cpp_info.components["mongocxx"].requires = ["mongo-c-driver::mongoc", "bsoncxx"]

        # bsoncxx
        bsoncxx_target = "bsoncxx_shared" if self.options.shared else "bsoncxx_static"
        self.cpp_info.components["bsoncxx"].set_property("cmake_target_name", f"mongo::{bsoncxx_target}")
        self.cpp_info.components["bsoncxx"].set_property("pkg_config_name", "libbsoncxx" if self.options.shared else "libbsoncxx-static")

        self.cpp_info.components["bsoncxx"].names["cmake_find_package"] = bsoncxx_target
        self.cpp_info.components["bsoncxx"].names["cmake_find_package_multi"] = bsoncxx_target

        self.cpp_info.components["bsoncxx"].libs = ["bsoncxx" if self.options.shared else "bsoncxx-static"]
        if not self.options.shared:
            self.cpp_info.components["bsoncxx"].defines = ["BSONCXX_STATIC"]
        self.cpp_info.components["bsoncxx"].requires = ["mongo-c-driver::bson"]
        if self.options.polyfill == "boost":
            self.cpp_info.components["bsoncxx"].requires.append("boost::headers")
