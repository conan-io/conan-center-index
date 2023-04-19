from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir, save
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


class AwsCIO(ConanFile):
    name = "aws-c-io"
    description = "IO and TLS for application protocols"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-io"
    topics = ("aws", "amazon", "cloud", "io", "tls",)
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # the versions of aws-c-common and aws-c-io are tied since aws-c-common/0.6.12 and aws-c-io/0.10.10
        # Please refer https://github.com/conan-io/conan-center-index/issues/7763
        if Version(self.version) <= "0.10.9":
            self.requires("aws-c-common/0.6.11")
            self.requires("aws-c-cal/0.5.11")
        else:
            self.requires("aws-c-common/0.8.2")
            self.requires("aws-c-cal/0.5.13")

        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.requires("s2n/1.3.31")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-io"))

        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"AWS::aws-c-io": "aws-c-io::aws-c-io"}
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
        self.cpp_info.set_property("cmake_file_name", "aws-c-io")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-io")
        self.cpp_info.libs = ["aws-c-io"]
        if self.options.shared:
            self.cpp_info.defines.append("AWS_IO_USE_IMPORT_EXPORT")
        if self.settings.os == "Macos":
            self.cpp_info.frameworks.append("Security")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["crypt32", "secur32", "shlwapi"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
