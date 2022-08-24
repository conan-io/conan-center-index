from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class VectorclassConan(ConanFile):
    name = "vectorclass"
    description = "C++ class library for using the Single Instruction Multiple " \
                  "Data (SIMD) instructions to improve performance on modern " \
                  "microprocessors with the x86 or x86/64 instruction set on " \
                  "Windows, Linux, and Mac platforms."
    license = "Apache-2.0"
    topics = ("conan", "vectorclass", "vector", "simd")
    homepage = "https://github.com/vectorclass/version2"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = ("os", "arch", "compiler", "build_type")
    options = {
        "fPIC": [True, False]
    }
    default_options = {
        "fPIC": True
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15.7",
            "gcc": "7",
            "clang": "4.0",
            "apple-clang": "9.1"
        }

    def validate(self):
        if self.settings.os not in ["Linux", "Windows", "Macos"] or self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration("vectorclass supports Linux/Windows/macOS and x86/x86_64 only.")

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 17)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warn("{} {} requires C++17. Your compiler is unknown. Assuming it supports C++17.".format(self.name, self.version))
        elif lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration("{} {} requires C++17, which your compiler does not support.".format(self.name, self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["vectorclass"]
