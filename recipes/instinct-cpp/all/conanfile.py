from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, replace_in_file, rm, rmdir
from conan.tools.microsoft import check_min_vs, is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "instinct-cpp"
    version = "0.1.5"
    description = ("instinct.cpp provides ready to use alternatives to OpenAI Assistant API a"
                   "nd built-in utilities for developing AI Agent applications (RAG, Chatbot, Code interpreter) powered by language models. "
                   "Call it langchain.cpp if you like.")
    license = "Apache-2.0"
    url = "https://github.com/RobinQu/instinct.cpp"
    homepage = "https://github.com/RobinQu/instinct.cpp"
    topics = ("LLM", "Agent", "GenAI")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_duckdb": [True, False],
        "with_exprtk": [True, False],
        "with_pdfium": [True, False],
        "with_duckx": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_duckdb": True,
        "with_exprtk": True,
        "with_pdfium": True,
        "with_duckx": True
    }

    @property
    def _min_cppstd(self):
        return 20

    # in case the project requires C++14/17/20/... the minimum compiler version should be listed
    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "15",
            "clang": "17",
            "gcc": "12"
        }

    # no exports_sources attribute, but export_sources(self) method instead
    # this allows finer grain exportation of patches per version
    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # for plain C projects only
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        # src_folder must use the same source folder name the project
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("hash-library/8.0", transitive_headers=True)
        self.requires("bshoshany-thread-pool/4.1.0", transitive_headers=True)

        if self.options.with_duckdb:
            self.requires("duckdb/0.10.2", options={"with_httpfs": True})

        self.requires("uriparser/0.9.7", transitive_headers=True)
        self.requires("crossguid/0.2.2", transitive_headers=True)
        self.requires("protobuf/5.27.0", transitive_headers=True)
        self.requires("reactiveplusplus/2.1.1", transitive_headers=True)
        self.requires("icu/74.1", options={"with_extras": True, "data_packaging": "static"})
        self.requires("tsl-ordered-map/1.1.0", transitive_headers=True)
        self.requires("fmt/10.2.1", transitive_headers=True)
        self.requires("fmtlog/2.2.1", transitive_headers=True)
        self.requires("nlohmann_json/3.11.3", transitive_headers=True)
        self.requires("base64/0.5.2", transitive_headers=True)
        self.requires("libcurl/8.6.0", transitive_headers=True)
        self.requires("inja/3.4.0", transitive_headers=True)
        self.requires("concurrentqueue/1.0.4", transitive_headers=True)
        self.requires("cpptrace/0.5.4", transitive_headers=True)

        if self.options.with_pdfium:
            self.requires("pdfium/95.0.4629", transitive_headers=True)

        if self.options.with_duckx:
            self.requires("duckx/1.2.2", transitive_headers=True)

        if self.options.with_exprtk:
            self.requires("exprtk/0.0.2", transitive_headers=True)

        self.requires("llama-cpp/b3040", transitive_headers=True)
        self.requires("cpp-httplib/0.15.3", transitive_headers=True)
        # deps of examples
        self.requires("cli11/2.4.1", transitive_headers=True)
        # test deps
        self.test_requires("gtest/1.14.0")

    def validate(self):
        # validate the minimum cpp standard supported. For C++ projects only
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        # in case it does not work in another configuration, it should validated here too
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        # BUILD_SHARED_LIBS and POSITION_INDEPENDENT_CODE are automatically parsed when self.options.shared or self.options.fPIC exist
        tc = CMakeToolchain(self)
        # Boolean values are preferred instead of "ON"/"OFF"
        tc.variables["PACKAGE_CUSTOM_DEFINITION"] = True
        if is_msvc(self):
            # don't use self.settings.compiler.runtime
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)

        tc.variables["WITH_DUCKDB"] = self.options.with_duckdb
        tc.variables["WITH_EXPRTK"] = self.options.with_exprtk
        tc.variables["WITH_PDFIUM"] = self.options.with_pdfium
        tc.variables["WITH_DUCKX"] = self.options.with_duckx
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()
        tc = VirtualBuildEnv(self)
        tc.generate(scope="build")

    # def _patch_sources(self):
    #     apply_conandata_patches(self)
    #     # remove bundled xxhash
    #     rm(self, "whateer.*", os.path.join(self.source_folder, "lib"))
    #     replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "...", "")

    def build(self):
        # self._patch_sources()  # It can be apply_conandata_patches(self) only in case no more patches are needed
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        # copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        #
        # # some files extensions and folders are not allowed. Please, read the FAQs to get informed.
        # rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # rmdir(self, os.path.join(self.package_folder, "share"))
        # rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        # rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        # rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["package_lib"]

        # if package has an official FindPACKAGE.cmake listed in https://cmake.org/cmake/help/latest/manual/cmake-modules.7.html#find-modules
        # examples: bzip2, freetype, gdal, icu, libcurl, libjpeg, libpng, libtiff, openssl, sqlite3, zlib...
        # self.cpp_info.set_property("cmake_module_file_name", "PACKAGE")
        # self.cpp_info.set_property("cmake_module_target_name", "PACKAGE::PACKAGE")
        # if package provides a CMake config file (package-config.cmake or packageConfig.cmake, with package::package target, usually installed in <prefix>/lib/cmake/<package>/)
        # self.cpp_info.set_property("cmake_file_name", "package")
        # self.cpp_info.set_property("cmake_target_name", "package::package")
        # # if package provides a pkgconfig file (package.pc, usually installed in <prefix>/lib/pkgconfig/)
        # self.cpp_info.set_property("pkg_config_name", "package")

        # If they are needed on Linux, m, pthread and dl are usually needed on FreeBSD too
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("dl")

        # # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        # self.cpp_info.filenames["cmake_find_package"] = "PACKAGE"
        # self.cpp_info.filenames["cmake_find_package_multi"] = "package"
        # self.cpp_info.names["cmake_find_package"] = "PACKAGE"
        # self.cpp_info.names["cmake_find_package_multi"] = "package"
        self.cpp_info.libs = ["proto"]
