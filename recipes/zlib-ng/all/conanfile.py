from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class ZlibNgConan(ConanFile):
    name = "zlib-ng"
    description = "zlib data compression library for the next generation systems"
    topics = ("zlib", "compression")
    license ="Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/zlib-ng/zlib-ng/"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "zlib_compat": [True, False],
        "with_gzfileop": [True, False],
        "with_optim": [True, False],
        "with_new_strategies": [True, False],
        "with_native_instructions": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "zlib_compat": False,
        "with_gzfileop": True,
        "with_optim": False,
        "with_new_strategies": True,
        "with_native_instructions": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def validate(self):
        if self.info.options.zlib_compat and not self.info.options.with_gzfileop:
            raise ConanInvalidConfiguration("The option 'with_gzfileop' must be True when 'zlib_compat' is True.")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ZLIB_ENABLE_TESTS"] = False
        tc.variables["ZLIB_COMPAT"] = self.options.zlib_compat
        tc.variables["WITH_GZFILEOP"] = self.options.with_gzfileop
        tc.variables["WITH_OPTIM"] = self.options.with_optim
        tc.variables["WITH_NEW_STRATEGIES"] = self.options.with_new_strategies
        tc.variables["WITH_NATIVE_INSTRUCTIONS"] = self.options.with_native_instructions
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        license_folder = os.path.join(self.package_folder, "licenses")
        copy(self, "LICENSE.md", src=self.source_folder, dst=license_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # upstream CMakeLists intentionally hardcodes install_name with full
        # install path (to match autootools behavior), instead of @rpath
        fix_apple_shared_install_name(self)

    def package_info(self):
        #FIXME: CMake targets are https://github.com/zlib-ng/zlib-ng/blob/29fd4672a2279a0368be936d7cd44d013d009fae/CMakeLists.txt#L914
        suffix = "" if self.options.zlib_compat else "-ng"
        self.cpp_info.set_property("pkg_config_name", f"zlib{suffix}")
        if self.settings.os == "Windows":
            # The library name of zlib-ng is complicated in zlib-ng>=2.0.4:
            # https://github.com/zlib-ng/zlib-ng/blob/2.0.4/CMakeLists.txt#L994-L1016
            base = "zlib" if is_msvc(self) or Version(self.version) < "2.0.4" or self.options.shared else "z"
            static_flag = "static" if is_msvc(self) and not self.options.shared and Version(self.version) >= "2.0.4" else ""
            build_type = "d" if self.settings.build_type == "Debug" else ""
            self.cpp_info.libs = [f"{base}{static_flag}{suffix}{build_type}"]
        else:
            self.cpp_info.libs = [f"z{suffix}"]
        if self.options.zlib_compat:
            self.cpp_info.defines.append("ZLIB_COMPAT")
        if self.options.with_gzfileop:
            self.cpp_info.defines.append("WITH_GZFILEOP")
        if not self.options.with_new_strategies:
            self.cpp_info.defines.extend(["NO_QUICK_STRATEGY", "NO_MEDIUM_STRATEGY"])
