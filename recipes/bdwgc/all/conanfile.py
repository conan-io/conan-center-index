from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.scm import Version
from conan.tools.files import apply_conandata_patches, get, save, rmdir, copy, load
from conan.errors import ConanException
import os

required_conan_version = ">=1.50.0"


class BdwGcConan(ConanFile):
    name = "bdwgc"
    homepage = "https://www.hboehm.info/gc/"
    description = "The Boehm-Demers-Weiser conservative C/C++ Garbage Collector (libgc, bdwgc, boehm-gc)"
    topics = ("gc", "garbage", "collector")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    _autotools_options_defaults = (
        ("cplusplus",                   False,),
        ("throw_bad_alloc_library",     True,),
        ("cord",                        True,),
        ("threads",                     True,),
        ("parallel_mark",               True,),
        ("handle_fork",                 True,),
        ("thread_local_alloc",          True,),
        ("threads_discovery",           True,),
        ("parallel_mark",               True,),
        ("gcj_support",                 True,),
        ("java_finalization",           True,),
        ("sigrt_signals",               False,),
        ("atomic_uncollectable",        True,),
        ("gc_debug",                    False,),
        ("redirect_malloc",             False,),
        ("disclaim",                    True,),
        ("large_config",                True,),
        ("gc_assertions",               False,),
        ("mmap",                        False,),
        ("munmap",                      True,),
        ("dynamic_loading",             True,),
        ("register_main_static_data",   True,),
        ("gc_assertions",               False,),
        ("checksums",                   False,),
        ("single_obj_compilation",      False,),
    )

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }
    for option, default in _autotools_options_defaults:
        options[option] = [True, False]
        default_options[option] = default

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        if Version(self.version) < "8.2.0":
            del self.options.throw_bad_alloc_library
        if not self.options.cplusplus:
            try:
                del self.settings.compiler.libcxx
            except Exception:
                pass
            try:
                del self.settings.compiler.cppstd
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("libatomic_ops/7.6.14")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        for option, _ in self._autotools_options_defaults:
            if option == "cord":
                tc.variables["build_cord"] = self.options.get_safe(option)
            elif option == "cplusplus":
                tc.cache_variables["enable_cplusplus"] = str(self.options.get_safe(option))
            else:
                tc.variables["enable_{}".format(option)] = self.options.get_safe(option)
        tc.variables["disable_gc_debug"] = not self.options.gc_debug
        tc.variables["disable_handle_fork"] = not self.options.handle_fork
        tc.variables["install_headers"] = True
        tc.variables["build_tests"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def _extract_copyright(self):
        readme_md = load(self, os.path.join(self.source_folder, "README.md"))
        copyright_header = "## Copyright & Warranty\n"
        index = readme_md.find(copyright_header)
        if index == -1:
            raise ConanException("Could not extract license from README file.")
        return readme_md[index+len(copyright_header):]

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "COPYRIGHT"), self._extract_copyright())
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "BDWgc")
        self.cpp_info.set_property("cmake_target_name", "BDWgc::BDWgc")

        # TODO: Remove on Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "BDWgc"
        self.cpp_info.names["cmake_find_package_multi"] = "BDWgc"

        self.cpp_info.components["gc"].set_property("cmake_target_name", "BDWgc::gc")
        self.cpp_info.components["gc"].set_property("pkg_config_name", "bdw-gc")
        self.cpp_info.components["gc"].libs = ["gc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["gc"].system_libs = ["pthread", "dl"]
        self.cpp_info.components["gc"].defines = ["GC_DLL" if self.options.shared else "GC_NOT_DLL"]
        if self.options.gc_debug:
            self.cpp_info.components["gc"].defines.append("GC_DEBUG")
        if self.settings.os == "Windows":
            self.cpp_info.components["gc"].requires = ["libatomic_ops::libatomic_ops"]

        if self.options.cplusplus and self.options.get_safe("throw_bad_alloc_library"):
            self.cpp_info.components["gctba"].set_property("cmake_target_name", "BDWgc::gctba")
            self.cpp_info.components["gctba"].libs = ["gctba"]
            self.cpp_info.components["gctba"].requires = ["gc"]

        if self.options.cplusplus:
            self.cpp_info.components["gccpp"].set_property("cmake_target_name", "BDWgc::gccpp")
            self.cpp_info.components["gccpp"].libs = ["gccpp"]
            self.cpp_info.components["gccpp"].requires = ["gc"]

        if self.options.cord:
            self.cpp_info.components["cord"].set_property("cmake_target_name", "BDWgc::cord")
            self.cpp_info.components["cord"].libs = ["cord"]
            self.cpp_info.components["cord"].requires = ["gc"]
