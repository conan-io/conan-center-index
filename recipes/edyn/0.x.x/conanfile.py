from conans import ConanFile, CMake, tools


class EdynConan(ConanFile):
    name = "edyn"
    license = "MIT"
    homepage = "https://github.com/xissburg/edyn"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Edyn is a real-time physics engine organized as an ECS. "
    topics = ("game-development", "physics-engine", "ecs",
              "entity-component-system", "entt")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake", "cmake_find_package", "cmake_paths"
    exports_sources = "src/**"

    @property
    def _source_subfolder(self):
        return "edyn"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        if tools.Version(self.version) < "0.2.0":
            self.requires("entt/3.5.2")
        else:
            self.requires("entt/3.8.0")

    def validate(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, minimal_cpp_standard)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses")
        for pattern in ("*.h", "*.hpp"):
            self.copy(pattern, dst="include", src="include")
            self.copy(pattern, dst="include", src="edyn/include")
        for pattern in ("*.a", "*.so", "*.dylib", "*.dll"):
            self.copy(pattern, dst="lib", keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["winmm"]
        elif self.settings.os == "Linux" or self.settings.os == "Macos":
            self.cpp_info.libs = ["pthread", "dl"]
        self.cpp_info.libs.append("Edyn")
        self.cpp_info.names["cmake_find_package"] = "Edyn"
        self.cpp_info.names["cmake_find_package_multi"] = "Edyn"
