from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get
from conan.tools.microsoft import is_msvc
from os.path import join

required_conan_version = ">=1.53.0"


class MiniSatConan(ConanFile):
    name = "minisat"
    description = "minimalistic SAT solver"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://minisat.se"
    topics = ("satisfiability", "solver")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def validate(self):
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        # https://github.com/niklasso/minisat/blob/37dc6c67e2af26379d88ce349eb9c4c6160e8543/minisat/utils/ParseUtils.h#L27
        self.requires("zlib/1.2.13", transitive_headers=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["STATIC_BINARIES"] = not self.options.shared
        tc.variables["USE_SORELEASE"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _determine_lib_name(self):
        return f"minisat-lib-{'shared' if self.options.shared else 'static'}"

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target=self._determine_lib_name())

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=join(self.package_folder, "licenses"))
        copy(self, pattern="*.h", src=join(self.source_folder, "minisat"), dst=join(self.package_folder, "include", "minisat"))
        if self.options.shared:
            copy(self, pattern="*.so*", src=self.build_folder, dst=join(self.package_folder, "lib"))
            copy(self, pattern="*.dylib*", src=self.build_folder, dst=join(self.package_folder, "lib"))
        else:
            copy(self, pattern="*.a", src=self.build_folder, dst=join(self.package_folder, "lib"))
            copy(self, pattern="*.lib", src=self.build_folder, dst=join(self.package_folder, "lib"), keep_path=False)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
            self.cpp_info.system_libs.append("pthread")
