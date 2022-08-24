from from conan import ConanFile, tools
from conans import CMake
from conans.errors import ConanException
import os

required_conan_version = ">=1.33.0"


class BdwGcConan(ConanFile):
    name = "bdwgc"
    homepage = "https://www.hboehm.info/gc/"
    description = "The Boehm-Demers-Weiser conservative C/C++ Garbage Collector (libgc, bdwgc, boehm-gc)"
    topics = ("conan", "gc", "garbage", "collector")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "CMakeLists.txt", "patches/**"
    generators = "cmake"

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

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if tools.Version(self.version) <= "8.0.6":
            del self.options.throw_bad_alloc_library
        if not self.options.cplusplus:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def requirements(self):
        if self.settings.os == "Windows":
            self.requires("libatomic_ops/7.6.10")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        for option, _ in self._autotools_options_defaults:
            self._cmake.definitions["enable_{}".format(option)] = self.options.get_safe(option)
        self._cmake.definitions["disable_gc_debug"] = not self.options.gc_debug
        self._cmake.definitions["disable_handle_fork"] = not self.options.handle_fork
        self._cmake.definitions["install_headers"] = True
        self._cmake.definitions["build_tests"] = False
        self._cmake.verbose = True
        self._cmake.parallel = False
        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _extract_copyright(self):
        readme_md = open(os.path.join(self._source_subfolder, "README.md")).read()
        copyright_header = "## Copyright & Warranty\n"
        index = readme_md.find(copyright_header)
        if index == -1:
            raise ConanException("Could not extract license from README file.")
        return readme_md[index+len(copyright_header):]

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "COPYRIGHT"), self._extract_copyright())
        cmake = self._configure_cmake()
        cmake.install()

    @property
    def _libs(self):
        libs = []
        if self.options.get_safe("throw_bad_alloc_library"):
            libs.append("gctba")
        if self.options.cplusplus:
            libs.append("gccpp")
        if self.options.cord:
            libs.append("cord")
        libs.append("gc")
        return libs

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "bdw-gc"
        self.cpp_info.libs = self._libs
        self.cpp_info.defines = ["GC_DLL" if self.options.shared else "GC_NOT_DLL"]
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["pthread", "dl"]
        if self.options.gc_debug:
            self.cpp_info.defines.append("GC_DEBUG")
