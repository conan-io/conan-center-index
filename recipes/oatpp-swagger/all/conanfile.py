from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os

required_conan_version = ">=1.51.1"


class OatppSwaggerConan(ConanFile):
    name = "oatpp-swagger"
    license = "Apache-2.0"
    homepage = "https://github.com/oatpp/oatpp-swagger"
    url = "https://github.com/conan-io/conan-center-index"
    description = "oat++ Swagger library"
    topics = ("oat++", "oatpp", "swagger")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires(f"oatpp/{self.version}")

    def validate(self):
        if self.info.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

        if is_msvc(self) and self.info.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared library with msvc")

        if self.info.settings.compiler == "gcc" and Version(self.info.settings.compiler.version) < "5":
            raise ConanInvalidConfiguration(f"{self.ref} requires GCC >=5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OATPP_BUILD_TESTS"] = False
        tc.variables["OATPP_MODULES_LOCATION"] = "INSTALLED"
        if Version(self.version) >= "1.3.0" and is_msvc(self):
            tc.variables["OATPP_MSVC_LINK_STATIC_RUNTIME"] = is_msvc_static_runtime(self)
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "oatpp-swagger")
        self.cpp_info.set_property("cmake_target_name", "oatpp::oatpp-swagger")
        # TODO: back to global scope in conan v2 once legacy generators removed
        self.cpp_info.components["_oatpp-swagger"].includedirs = [
            os.path.join("include", f"oatpp-{self.version}", "oatpp-swagger")
        ]
        self.cpp_info.components["_oatpp-swagger"].libdirs = [os.path.join("lib", f"oatpp-{self.version}")]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["_oatpp-swagger"].bindirs = [os.path.join("bin", f"oatpp-{self.version}")]
        else:
            self.cpp_info.components["_oatpp-swagger"].bindirs = []
        self.cpp_info.components["_oatpp-swagger"].libs = ["oatpp-swagger"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_oatpp-swagger"].system_libs = ["pthread"]
        # export env var
        res_path = os.path.join(self.package_folder, "include", f"oatpp-{self.version}", "bin", "oatpp-swagger", "res")
        self.runenv_info.prepend_path("OATPP_SWAGGER_RES_PATH", res_path)

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.filenames["cmake_find_package"] = "oatpp-swagger"
        self.cpp_info.filenames["cmake_find_package_multi"] = "oatpp-swagger"
        self.cpp_info.names["cmake_find_package"] = "oatpp"
        self.cpp_info.names["cmake_find_package_multi"] = "oatpp"
        self.cpp_info.components["_oatpp-swagger"].names["cmake_find_package"] = "oatpp-swagger"
        self.cpp_info.components["_oatpp-swagger"].names["cmake_find_package_multi"] = "oatpp-swagger"
        self.cpp_info.components["_oatpp-swagger"].set_property("cmake_target_name", "oatpp::oatpp-swagger")
        self.cpp_info.components["_oatpp-swagger"].requires = ["oatpp::oatpp"]
        self.env_info.OATPP_SWAGGER_RES_PATH = res_path
