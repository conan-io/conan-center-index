from conan import ConanFile
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.53.0"


class AwsCCal(ConanFile):
    name = "aws-c-cal"
    description = "Aws Crypto Abstraction Layer: Cross-Platform, C99 wrapper for cryptography primitives."
    topics = ("aws", "amazon", "cloud", "cal", "crypt", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/awslabs/aws-c-cal"
    license = "Apache-2.0"
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
    def _needs_openssl(self):
        return not (self.settings.os == "Windows" or is_apple_os(self))

    def export_sources(self):
        export_conandata_patches(self)

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
        if Version(self.version) <= "0.5.11":
            # transitive_libs probably not strictly required, but it's impossible to write a robust test package
            # without it for conan v2 (we would have to required aws-c-common in test package, but we can't know
            # which version to require in test package)
            self.requires("aws-c-common/0.6.11", transitive_headers=True, transitive_libs=True)
        else:
            self.requires("aws-c-common/0.8.2", transitive_headers=True, transitive_libs=True)
        if self._needs_openssl:
            self.requires("openssl/[>=1.1 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["USE_OPENSSL"] = self._needs_openssl
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "aws-c-cal"))

        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"AWS::aws-c-cal": "aws-c-cal::aws-c-cal"}
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
        self.cpp_info.set_property("cmake_file_name", "aws-c-cal")
        self.cpp_info.set_property("cmake_target_name", "AWS::aws-c-cal")
        self.cpp_info.libs = ["aws-c-cal"]
        self.cpp_info.requires = ["aws-c-common::aws-c-common"]
        if self.options.shared:
            self.cpp_info.defines.append("AWS_CAL_USE_IMPORT_EXPORT")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ncrypt")
        elif is_apple_os(self):
            self.cpp_info.frameworks.extend(["CoreFoundation", "Security"])
        elif self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("dl")

        if self._needs_openssl:
            self.cpp_info.requires.append("openssl::crypto")
            if not self.dependencies["openssl"].options.shared:
                # aws-c-cal does not statically link to openssl and searches dynamically for openssl symbols .
                # Mark these as undefined so the linker will include them.
                # This avoids dynamical look-up for a system crypto library.
                crypto_symbols = [
                    "HMAC_Update", "HMAC_Final", "HMAC_Init_ex",
                ]
                if Version(self.dependencies["openssl"].ref.version) >= "1.1":
                    crypto_symbols.extend([
                        "HMAC_CTX_new", "HMAC_CTX_free", "HMAC_CTX_reset",
                    ])
                else:
                    crypto_symbols.extend([
                        "HMAC_CTX_init", "HMAC_CTX_cleanup", "HMAC_CTX_reset",
                    ])
                crypto_link_flags = "-Wl," + ",".join(f"-u{symbol}" for symbol in crypto_symbols)
                self.cpp_info.exelinkflags.append(crypto_link_flags)
                self.cpp_info.sharedlinkflags.append(crypto_link_flags)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
