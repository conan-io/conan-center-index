import glob
import os
import shutil

from conans import ConanFile, CMake, tools

class CjsonConan(ConanFile):
    name = "cjson"
    description = "Ultralightweight JSON parser in ANSI C."
    license = "MIT"
    topics = ("conan", "cjson", "json", "parser")
    homepage = "https://github.com/DaveGamble/cJSON"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_locales": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_locales": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("cJSON-" + self.version, self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ENABLE_SANITIZERS"] = False
        self._cmake.definitions["ENABLE_SAFE_STACK"] = False
        self._cmake.definitions["ENABLE_PUBLIC_SYMBOLS"] = True
        self._cmake.definitions["ENABLE_HIDDEN_SYMBOLS"] = False
        self._cmake.definitions["ENABLE_TARGET_EXPORT"] = False
        self._cmake.definitions["BUILD_SHARED_AND_STATIC_LIBS"] = False
        self._cmake.definitions["CJSON_OVERRIDE_BUILD_SHARED_LIBS"] = False
        self._cmake.definitions["ENABLE_CJSON_UTILS"] = False
        self._cmake.definitions["ENABLE_CJSON_TEST"] = False
        self._cmake.definitions["ENABLE_LOCALES"] = self.options.use_locales
        self._cmake.definitions["ENABLE_FUZZING"] = False
        # Disable Custom Compiler Flags for MingW on Windows, because it uses -fstack-protector-strong
        self._cmake.definitions["ENABLE_CUSTOM_COMPILER_FLAGS"] = not (self.settings.os == "Windows" and self.settings.compiler == "gcc")

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        self._move_dll_to_bin_folder()

    def _move_dll_to_bin_folder(self):
        if self.settings.os == "Windows" and self.options.shared:
            bin_dir = os.path.join(self.package_folder, "bin")
            if not os.path.exists(bin_dir):
                os.mkdir(bin_dir)
            for dll_file in glob.glob(os.path.join(self.package_folder, "lib", "*.dll")):
                shutil.move(dll_file, bin_dir)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
