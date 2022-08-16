from conans import CMake, ConanFile, tools
import functools

required_conan_version = ">=1.33.0"


class LibuclConan(ConanFile):
    name = "libucl"
    description = "Universal configuration library parser"
    license = "BSD-2-Clause"
    homepage = "https://github.com/vstakhov/libucl"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("universal", "configuration", "language", "parser", "ucl")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_url_include": [True, False],
        "enable_url_sign": [True, False],
        "with_lua": [False, "lua", "luajit"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_url_include": False,
        "enable_url_sign": False,
        "with_lua": False,
    }

    generators = "cmake", "cmake_find_package_multi"
    exports_sources = "CMakeLists.txt", "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.enable_url_include:
            self.requires("libcurl/7.84.0")
        if self.options.enable_url_sign:
            self.requires("openssl/1.1.1q")
        if self.options.with_lua == "lua":
            self.requires("lua/5.4.4")
        elif self.options.with_lua == "luajit":
            self.requires("luajit/2.0.5")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        on_off = lambda v: "ON" if v else "OFF"
        cmake.definitions["ENABLE_URL_INCLUDE"] = on_off(self.options.enable_url_include)
        cmake.definitions["ENABLE_URL_SIGN"] = on_off(self.options.enable_url_sign)
        cmake.definitions["ENABLE_LUA"] = on_off(self.options.with_lua == "lua")
        cmake.definitions["ENABLE_LUAJIT"] = on_off(self.options.with_lua == "luajit")
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses", keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ucl"]
        self.cpp_info.names["pkg_config"] = "libucl"
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("UCL_STATIC")
