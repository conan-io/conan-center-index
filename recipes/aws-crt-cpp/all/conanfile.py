from conan import ConanFile
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir, save
from conan.tools.build import check_min_cppstd
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

import os
import textwrap

required_conan_version = ">=1.53.0"


class AwsCrtCpp(ConanFile):
    name = "aws-crt-cpp"
    description = "C++ wrapper around the aws-c-* libraries. Provides Cross-Platform Transport Protocols and SSL/TLS implementations for C++."
    license = "Apache-2.0",
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-crt-cpp"
    topics = ("aws", "amazon", "cloud", "wrapper")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return "11"

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
        if self.version == "0.26.9":
            # From add_subdirectory() calls in https://github.com/awslabs/aws-crt-cpp/blob/v0.26.9/CMakeLists.txt
            self.requires("aws-c-common/0.9.15")
            self.requires("aws-c-sdkutils/0.1.15")
            self.requires("aws-c-io/0.14.7", transitive_headers=True)
            self.requires("aws-c-cal/0.6.14")
            self.requires("aws-c-compression/0.2.18")
            self.requires("aws-c-http/0.8.1", transitive_headers=True)
            self.requires("aws-c-auth/0.7.16", transitive_headers=True)
            self.requires("aws-c-mqtt/0.10.3", transitive_headers=True)
            self.requires("aws-checksums/0.1.18")
            self.requires("aws-c-event-stream/0.4.2")
            self.requires("aws-c-s3/0.5.5")
        if self.version == "0.17.1a":
            # From add_subdirectory() calls in https://github.com/awslabs/aws-crt-cpp/blob/v0.17.1a/CMakeLists.txt#L95
            self.requires("aws-c-http/0.6.7", transitive_headers=True)
            self.requires("aws-c-mqtt/0.7.8", transitive_headers=True)
            self.requires("aws-c-cal/0.5.12")
            self.requires("aws-c-compression/0.2.14")
            self.requires("aws-c-auth/0.6.4", transitive_headers=True)
            self.requires("aws-c-common/0.6.11")
            self.requires("aws-c-io/0.10.9", transitive_headers=True)
            self.requires("aws-checksums/0.1.12")
            self.requires("aws-c-event-stream/0.2.7")
            self.requires("aws-c-s3/0.1.26")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if is_msvc(self):
            tc.variables["AWS_STATIC_MSVC_RUNTIME_LIBRARY"] = is_msvc_static_runtime(self)
        tc.variables["BUILD_TESTING"] = False
        tc.cache_variables["BUILD_DEPS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-crt-cpp"))

        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"AWS::aws-crt-cpp": "aws-crt-cpp::aws-crt-cpp"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "aws-crt-cpp")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-crt-cpp")
        self.cpp_info.libs = ["aws-crt-cpp"]
        if self.options.shared:
            self.cpp_info.defines.append("AWS_CRT_CPP_USE_IMPORT_EXPORT")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
