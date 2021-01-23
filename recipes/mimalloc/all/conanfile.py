from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class MimallocConan(ConanFile):
    name = "mimalloc"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/mimalloc"
    description = "mimalloc is a compact general purpose allocator with excellent performance."
    topics = ("conan", "mimalloc", "allocator", "performance", "microsoft")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "secure": [True, False],
        "override": [True, False],
        "inject": [True, False],
        "single_object": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "secure": False,
        "override": False,
        "inject": False,
        "single_object": False
    }
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/*"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "Visual Studio": "15",
            "clang": "5",
            "apple-clang": "10",
        }

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

            # single_object is valid only for static
            # override:
            if self.options.get_safe("single_object"):
                del self.options.single_object

        # inject is valid only for Unix-like dynamic override:
        if not self.options.shared and self.options.get_safe("inject"):
            del self.options.inject

        # single_object and inject are valid only when
        # overriding on Unix-like platforms:
        if not self.options.override:
            if self.options.get_safe("single_object"):
                del self.options.single_object
            if self.options.get_safe("inject"):
                del self.options.inject

        # Shared overriding requires dynamic runtime for MSVC:
        if self.options.override and \
           self.options.shared and \
           self.settings.compiler == "Visual Studio" and \
           "MT" in str(self.settings.compiler.runtime):
            raise ConanInvalidConfiguration(
                "Dynamic runtime (MD/MDd) is required when using mimalloc as a shared library for override")

        if self.options.override and \
           self.options.get_safe("single_object") and \
           self.options.get_safe("inject"):
            raise ConanInvalidConfiguration("Single object is incompatible with library injection");

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)

        if not minimum_version:
            self.output.warn("mimalloc requires C++17. Your compiler is unknown. Assuming it supports C++17.")
        elif tools.Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("mimalloc requires a compiler that supports at least C++17")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("mimalloc-" + self.version, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        # single_object and inject are options
        # only when overriding on Unix-like platforms:
        if self.settings.compiler == "Visual Studio":
            del self.options.single_object
            del self.options.inject

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self._cmake.is_multi_configuration:
            self._cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
        self._cmake.definitions["MI_BUILD_TESTS"] = "OFF"
        self._cmake.definitions["MI_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["MI_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["MI_BUILD_OBJECT"] = self.options.get_safe("single_object", False)
        self._cmake.definitions["MI_OVERRIDE"] = "ON" if self.options.override else "OFF"
        self._cmake.definitions["MI_SECURE"] = "ON" if self.options.secure else "OFF"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.compiler == "Visual Studio" and self.settings.arch == "x86":
            tools.replace_path_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                                       "mimalloc-redirect.lib", "mimalloc-redirect32.lib")
        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            cmake = self._configure_cmake()
            cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        with tools.vcvars(self.settings) if self.settings.compiler == "Visual Studio" else tools.no_op():
            cmake = self._configure_cmake()
            cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "cmake"))

        if self.options.get_safe("single_object"):
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"),
                                       "*.a")
            shutil.move(os.path.join(self.package_folder, self._obj_name + ".o"),
                        os.path.join(self.package_folder, "lib"))
            shutil.copy(os.path.join(self.package_folder, "lib", self._obj_name + ".o"),
                        os.path.join(self.package_folder, "lib", self._obj_name))

        if self.settings.os == "Windows" and self.options.shared:
            if self.settings.arch == "x86_64":
                self.copy("mimalloc-redirect.dll", src=os.path.join(self._source_subfolder, "bin"),
                          dst="bin")
            elif self.settings.arch == "x86":
                self.copy("mimalloc-redirect32.dll", src=os.path.join(self._source_subfolder, "bin"),
                          dst="bin")

    @property
    def _obj_name(self):
        name = "mimalloc"
        if self.options.secure:
            name += "-secure"
        if self.settings.build_type not in ("Release", "RelWithDebInfo", "MinSizeRel"):
            name += "-{}".format(str(self.settings.build_type).lower())
        return name

    @property
    def _lib_name(self):
        name = "mimalloc" if self.settings.os == "Windows" else "libmimalloc"

        if self.settings.os == "Windows" and not self.options.shared:
            name += "-static"
        if self.options.secure:
            name += "-secure"
        if self.settings.build_type not in ("Release", "RelWithDebInfo", "MinSizeRel"):
            name += "-{}".format(str(self.settings.build_type).lower())
        return name

    def package_info(self):
        if self.options.get_safe("inject"):
            self.cpp_info.includedirs = []
            self.cpp_info.libdirs = []
            self.cpp_info.resdirs = []
            return

        if self.options.get_safe("single_object"):
            obj_ext = "o"
            obj_file = "{}.{}".format(self._obj_name, obj_ext)
            obj_path = os.path.join(self.package_folder, "lib", obj_file)
            self.cpp_info.exelinkflags = [obj_path]
            self.cpp_info.sharedlinkflags = [obj_path]
            self.cpp_info.libdirs = []
            self.cpp_info.bindirs = []
        else:
            self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs.extend(["psapi", "shell32", "user32", "bcrypt"])
            elif self.settings.os == "Linux":
                self.cpp_info.system_libs.append("rt")
