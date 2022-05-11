from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"

class TcfAgentConan(ConanFile):
    name = "libtcf"
    license = "BSD-3-Clause"
    homepage = "https://git.eclipse.org/c/tcf/org.eclipse.tcf.agent.git/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Eclipse target communication framework agent"
    topics = ("debugging", "tracing")
    settings = "os", "compiler", "build_type", "arch"
    options = {
            "shared": [True, False],
            "fPIC": [True, False],
    }
    default_options = {
            "shared": False,
            "fPIC": True,
    }

    generators = "cmake"
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

    def validate(self):
        pass

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
               strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if self.settings.os == "Windows":
            del self.options.fPIC
            self._cmake.definitions["TCF_OPSYS"]="Windows"
        if self.settings.os == "Linux":
            self._cmake.definitions["TCF_OPSYS"]="GNU/Linux"
        if self.settings.os == "FreeBSD":
            self._cmake.definitions["TCF_OPSYS"]="FreeBSD"
        if self.settings.os == "Macos":
            self._cmake.definitions["TCF_OPSYS"]="Darwin"

        self._cmake.definitions["TCF_MACHINE"]=self.settings.arch
        self._cmake.configure()
        return self._cmake

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["libtcf"]
        self.cpp_info.set_property("cmake_file_name", "libtcf")
        self.cpp_info.set_property("cmake_target_name", "libtcf::libtcf")

