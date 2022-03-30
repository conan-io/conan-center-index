from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class FunchookConan(ConanFile):
    name = "funchook"
    homepage = "https://github.com/kubo/funchook"
    description = " Hook function calls by inserting jump instructions at runtime"
    topics = ("function", "hooking")
    url = "https://github.com/conan-io/conan-center-index"
    license = "GPL-2.0-or-later-linking-exception"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "disassembler": ["diStorm3", "zydis", "capstone"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "disassembler": "diStorm3",
    }

    _cmake = None

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        if self.options.disassembler == "capstone":
            self.requires("capstone/4.0.2")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.options.disassembler == "zydis":
            raise ConanInvalidConfiguration("disassembler 'zydis' currently not supported by this Conan recipe")
        if 'arm' in str(self.settings.arch):
            if self.settings.os == "Macos":
                raise ConanInvalidConfiguration("Funchook does not support ARM on MacOS")
            if self.options.disassembler != "capstone":
                raise ConanInvalidConfiguration("disassembler must be 'capstone' for arm arch")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["FUNCHOOK_BUILD_TESTS"] = False
        self._cmake.definitions["FUNCHOOK_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["FUNCHOOK_BUILD_STATIC"] = not self.options.shared
        if self.options.disassembler == "diStorm3":
            self._cmake.definitions["FUNCHOOK_DISASM"] = "distorm"
        else:
            self._cmake.definitions["FUNCHOOK_DISASM"] = self.options.disassembler
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["funkhook"]

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["m", "dl"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["psapi"])
