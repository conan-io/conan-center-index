from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=1.53.0"

class SquirrelConan(ConanFile):
    name = "squirrel"
    description = "Squirrel is a high level imperative, object-oriented programming " \
                  "language, designed to be a light-weight scripting language that " \
                  "fits in the size, memory bandwidth, and real-time requirements " \
                  "of applications like video games."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.squirrel-lang.org/"
    topics = ("programming-language", "object-oriented", "scripting")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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

    def validate(self):
        if Version(self.version) <= "3.1":
            if is_apple_os(self):
                raise ConanInvalidConfiguration(f"{self.ref} and earlier does not support Macos")
            if self.settings.compiler == "clang":
                compiler_version = Version(self.settings.compiler.version)
                if compiler_version < "9" or compiler_version >= "11":
                    raise ConanInvalidConfiguration(
                        f"{self.ref} and earlier does not support Clang {compiler_version}"
                    )
            if self.settings.compiler == "gcc":
                compiler_version = Version(self.settings.compiler.version)
                if compiler_version >= "12":
                    raise ConanInvalidConfiguration(
                        f"{self.ref} and earlier does not support gcc {compiler_version}"
                    )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DISABLE_DYNAMIC"] = not self.options.shared
        tc.variables["DISABLE_STATIC"] = self.options.shared
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="COPYRIGHT", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "squirrel")
        # CMakeDeps generator uses the global target if a downstream recipe depends on squirrel globally,
        # and squirrel::squirrel is stolen by libsquirrel component (if shared) which doesn't depend on all other components.
        # So this unofficial target is created as a workaround.
        self.cpp_info.set_property("cmake_target_name", "squirrel::squirel-all-do-not-use")

        suffix = "" if self.options.shared else "_static"

        # squirrel
        self.cpp_info.components["libsquirrel"].set_property("cmake_target_name", f"squirrel::squirrel{suffix}")
        self.cpp_info.components["libsquirrel"].libs = [f"squirrel{suffix}"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libsquirrel"].system_libs.append("m")

        # sqstdlib
        self.cpp_info.components["sqstdlib"].set_property("cmake_target_name", f"squirrel::sqstdlib{suffix}")
        self.cpp_info.components["sqstdlib"].libs = [f"sqstdlib{suffix}"]
        self.cpp_info.components["sqstdlib"].requires = ["libsquirrel"]

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH env var : {binpath}")
        self.env_info.PATH.append(binpath)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libsquirrel"].names["cmake_find_package"] = f"squirrel{suffix}"
        self.cpp_info.components["libsquirrel"].names["cmake_find_package_multi"] = f"squirrel{suffix}"
        self.cpp_info.components["sqstdlib"].names["cmake_find_package"] = f"sqstdlib{suffix}"
        self.cpp_info.components["sqstdlib"].names["cmake_find_package_multi"] = f"sqstdlib{suffix}"
