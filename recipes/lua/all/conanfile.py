from conans import ConanFile, CMake, tools
import os

class LuaConan(ConanFile):
    name = "lua"
    description = "Lua is a powerful, efficient, lightweight, embeddable scripting language."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.lua.org/"
    topics = ("conan", "lua", "scripting")
    license = "MIT"
    generators = "cmake"
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = ["CMakeLists.txt"]

    _source_subfolder = "source_subfolder"

    options = {"shared": [False, True], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "lua-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["SOURCE_SUBDIR"] = self._source_subfolder
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        # Extract the License/s from the header to a file
        tmp = tools.load( os.path.join( self._source_subfolder, "src", "lua.h") )
        license_contents = tmp[tmp.find("/***", 1):tmp.find("****/", 1)]

        os.makedirs(os.path.join(self.package_folder, "licenses"))
        tools.save(os.path.join(self.package_folder, "licenses", "COPYING.txt"), license_contents)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append("include/lua")
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
