from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


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
        "single_object": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "secure": False,
        "override": False,
        "single_object": False
    }
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/*"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("mimalloc-" + self.version, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        tools.check_min_cppstd(self, "14")
        if self.options.shared:
            del self.options.fPIC

        if self.options.shared or self.settings.compiler == "Visual Studio":
            del self.options.single_object

        if self.options.override:
            if self.options.shared and self.settings.compiler == "Visual Studio" and \
                    "MT" in str(self.settings.compiler.runtime):
                raise ConanInvalidConfiguration(
                    "Cannot use MT(d) runtime when building mimalloc as a shared library for override")

    _cmake = None

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.settings.compiler == "Visual Studio":
            self._cmake.generator = "NMake Makefiles"
        self._cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
        self._cmake.definitions["MI_BUILD_TESTS"] = "OFF"
        self._cmake.definitions["MI_BUILD_SHARED"] = "ON" if self.options.shared else "OFF"
        self._cmake.definitions["MI_BUILD_STATIC"] = "ON" if not self.options.shared and \
                                                             not self.options.get_safe("single_object", False) else "OFF"
        self._cmake.definitions["MI_BUILD_OBJECT"] = "ON" if self.options.get_safe("single_object") else "OFF"
        self._cmake.definitions["MI_OVERRIDE"] = "ON" if self.options.override else "OFF"
        self._cmake.definitions["MI_SECURE"] = "ON" if self.options.secure else "OFF"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
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

        if self.settings.os == "Windows" and self.options.override and self.options.shared:
            if self.settings.arch == "x86_64":
                self.copy("mimalloc-redirect.dll", src=os.path.join(self._source_subfolder, "bin"),
                          dst=self._install_prefix)
            elif self.settings.arch == "x86":
                self.copy("mimalloc-redirect32.dll", src=os.path.join(self._source_subfolder, "bin"),
                          dst=self._install_prefix)

        tools.rmdir(os.path.join(self.package_folder, self._install_prefix, "cmake"))

    @property
    def _install_prefix(self):
        version = tools.Version(self.version)
        return os.path.join("lib", "{}-{}.{}".format(self.name, version.major, version.minor))

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
        name = "mimalloc"
        if self.settings.os == "Windows" and not self.options.shared:
            name += "-static"
        if self.options.secure:
            name += "-secure"
        if self.settings.build_type not in ("Release", "RelWithDebInfo", "MinSizeRel"):
            name += "-{}".format(str(self.settings.build_type).lower())
        return name

    def package_info(self):
        self.cpp_info.includedirs = [os.path.join(self._install_prefix, "include")]
        if self.options.get_safe("single_object"):
            obj_ext = "obj" if self.settings.os == "Windows" else "o"
            obj_file = "{}.{}".format(self._obj_name, obj_ext)
            obj_path = os.path.join(self.package_folder, self._install_prefix, obj_file)
            self.cpp_info.exelinkflags = [obj_path]
            self.cpp_info.libdirs = []
            self.cpp_info.bindirs = []
        else:
            self.cpp_info.libs = [self._lib_name]
            self.cpp_info.libdirs = [self._install_prefix]
            self.cpp_info.bindirs = [self._install_prefix]

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
        if not self.options.shared:
            if self.settings.os == "Windows":
                self.cpp_info.system_libs.extend(["psapi", "shell32", "user32", "bcrypt"])
            elif self.settings.os == "Linux":
                self.cpp_info.system_libs.append("rt")
