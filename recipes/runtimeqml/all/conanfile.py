from conan import ConanFile
from conan.tools.cmake import CMake
from conan.tools.files import get, copy
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.49.0"

class RuntimeQml(ConanFile):
    name = "runtimeqml"
    homepage = "https://github.com/GIPdA/runtimeqml"
    description = "Enables hot-reloading qml files"
    topics = ("qt", "hot-reload", "qml", "gui")
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    generators = "CMakeDeps", "CMakeToolchain"

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)],
            destination=self.source_folder, strip_root=True)

    def requirements(self):
        if self.version == "cci.20211220": # Only version which supports qt5
            self.requires("qt/5.15.5")
        else:
            self.requires("qt/6.3.1")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        qt = self.dependencies["qt"]
        if not qt.options.qtdeclarative:
            raise ConanInvalidConfiguration(f"{self.ref} requires option qt:qtdeclarative=True")

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self.source_folder,
                  dst="licenses", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)
        self.copy(pattern="*.so", dst="lib", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.h*", src=self.source_folder,
                  dst="include", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["runtimeqml"]
