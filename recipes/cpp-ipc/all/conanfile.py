from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class CppIPCConan(ConanFile):
    name = "cpp-ipc"
    description = "C++ IPC Library: A high-performance inter-process communication using shared memory on Linux/Windows."
    topics = ("ipc", "shared memory", )
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/mutouyun/cpp-ipc"
    license = "MIT",
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt"]
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "cmake"

    _compiler_required_cpp17 = {
        "Visual Studio": "17",
        "gcc": "8",
        "clang": "4",
    }

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
        if tools.is_apple_os(self.settings.os):
            raise ConanInvalidConfiguration("{} does not support Apple platform".format(self.name))

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)

        minimum_version = self._compiler_required_cpp17.get(str(self.settings.compiler), False)
        if minimum_version:
            if tools.Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration("{} requires C++17, which your compiler does not support.".format(self.name))
        else:
            self.output.warn("{0} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name))

        if self.settings.compiler == "clang" and self.settings.compiler.get_safe("libcxx") == "libc++":
            raise ConanInvalidConfiguration("{} doesn't support clang with libc++".format(self.name))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
            destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["LIBIPC_BUILD_SHARED_LIBS"] = self.options.shared
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["ipc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["rt", "pthread"]
