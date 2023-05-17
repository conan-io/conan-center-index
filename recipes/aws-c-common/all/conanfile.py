from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


class AwsCCommon(ConanFile):
    name = "aws-c-common"
    description = (
        "Core c99 package for AWS SDK for C. Includes cross-platform "
        "primitives, configuration, data structures, and error handling."
    )
    topics = ("aws", "amazon", "cloud", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-common"
    license = "Apache-2.0"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cpu_extensions": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cpu_extensions": True,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "0.6.11":
            del self.options.cpu_extensions

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.options.shared and is_msvc(self) and is_msvc_static_runtime(self):
            raise ConanInvalidConfiguration("Static runtime + shared is not working for more recent releases")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["AWS_ENABLE_LTO"] = False
        if Version(self.version) >= "0.6.0":
            tc.variables["AWS_WARNINGS_ARE_ERRORS"] = False
        if is_msvc(self):
            tc.variables["STATIC_CRT"] = is_msvc_static_runtime(self)
        tc.variables["USE_CPU_EXTENSIONS"] = self.options.get_safe("cpu_extensions", False)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-common"))

        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"AWS::aws-c-common": "aws-c-common::aws-c-common"}
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
        self.cpp_info.set_property("cmake_file_name", "aws-c-common")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-common")
        self.cpp_info.libs = ["aws-c-common"]
        if self.options.shared:
            self.cpp_info.defines.append("AWS_COMMON_USE_IMPORT_EXPORT")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl", "m", "pthread", "rt"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs = ["bcrypt", "ws2_32"]
            if Version(self.version) >= "0.6.13":
                self.cpp_info.system_libs.append("shlwapi")
        if not self.options.shared:
            if is_apple_os(self):
                self.cpp_info.frameworks = ["CoreFoundation"]
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
