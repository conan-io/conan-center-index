from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import collect_libs, copy, get
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.scm import Version
from os.path import join

required_conan_version = ">=1.53.0"


class SoPlexConan(ConanFile):
    name = "soplex"
    description = "SoPlex linear programming solver"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://soplex.zib.de"
    topics = ("simplex", "solver", "linear", "programming")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_boost": [True, False],
        "with_gmp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_boost": True,
        "with_gmp": True
    }

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "clang": "4",
            "apple-clang": "7",
        }

    def _determine_lib_name(self):
        if self.options.shared:
            return "soplexshared"
        elif self.options.get_safe("fPIC"):
            return "soplex-pic"
        else:
            return "soplex"

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        check_min_vs(self, 191)
        if not is_msvc(self):
            minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
            if minimum_version and Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
                )
        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} can not be built as shared on Visual Studio and msvc.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("zlib/1.2.13", transitive_headers=True)
        if self.options.with_gmp:
            # transitive libs as anything using soplex requires __gmpz_init_set_si
            # see https://github.com/conan-io/conan-center-index/pull/16017#issuecomment-1495688452
            self.requires("gmp/6.2.1", transitive_headers=True, transitive_libs=True)
        if self.options.with_boost:
            self.requires("boost/1.81.0", transitive_headers=True)  # also update Boost_VERSION_MACRO below!

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GMP"] = self.options.with_gmp
        tc.variables["BOOST"] = self.options.with_boost
        tc.variables["Boost_VERSION_MACRO"] = "108100"
        if self.options.with_gmp:
            tc.cache_variables["GMP_INCLUDE_DIRS"] = ";".join(self.dependencies["gmp"].cpp_info.includedirs)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target=f"lib{self._determine_lib_name()}")

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=join(self.package_folder, "licenses"))
        copy(self, pattern="soplex.h", src=join(self.source_folder, "src"), dst=join(self.package_folder, "include"))
        copy(self, pattern="soplex.hpp", src=join(self.source_folder, "src"), dst=join(self.package_folder, "include"))
        copy(self, pattern="soplex_interface.h", src=join(self.source_folder, "src"), dst=join(self.package_folder, "include"))
        copy(self, pattern="*.h", src=join(self.source_folder, "src", "soplex"), dst=join(self.package_folder, "include", "soplex"))
        copy(self, pattern="*.hpp", src=join(self.source_folder, "src", "soplex"), dst=join(self.package_folder, "include", "soplex"))
        copy(self, pattern="*.h", src=join(self.build_folder, "soplex"), dst=join(self.package_folder, "include", "soplex"))
        if self.options.shared:
            copy(self, pattern="*.so*", src=join(self.build_folder, "lib"), dst=join(self.package_folder, "lib"))
            copy(self, pattern="*.dylib*", src=join(self.build_folder, "lib"), dst=join(self.package_folder, "lib"))
        else:
            copy(self, pattern="*.a", src=join(self.build_folder, "lib"), dst=join(self.package_folder, "lib"))
            copy(self, pattern="*.lib", src=join(self.build_folder, "lib"), dst=join(self.package_folder, "lib"), keep_path=False)
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        # https://github.com/conan-io/conan-center-index/pull/16017#discussion_r1156484737
        self.cpp_info.set_property("cmake_target_name", "soplex")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
