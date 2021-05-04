import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.28.0"

class GoogleCloudCppConan(ConanFile):
    name = "google-cloud-cpp"
    description = "C++ Client Libraries for Google Cloud Services"
    license = "Apache-2.0"
    topics = "google", "cloud", "google-cloud-storage", "google-cloud-platform", "google-cloud-pubsub", "google-cloud-spanner", "google-cloud-bigtable"
    homepage = "https://github.com/googleapis/google-cloud-cpp"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package_multi", "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False]
        }
    default_options = {
        "shared": False, 
        "fPIC": True
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
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def validate(self):
        if self.settings.compiler == 'gcc' and tools.Version(self.settings.compiler.version) < "5.4":
            raise ConanInvalidConfiguration("Building requires GCC >= 5.4")
        if self.settings.compiler == 'clang' and tools.Version(self.settings.compiler.version) < "3.8":
            raise ConanInvalidConfiguration("Building requires clang >= 3.8")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def requirements(self):
        self.requires('protobuf/3.15.5')
        self.requires('grpc/1.37.1')
        self.requires('nlohmann_json/3.9.1')
        self.requires('crc32c/1.1.1')
        # if bigquery, bigtable, logging, iam, spanner, pubsub, generator
        #   self.requires("gRPC")
        #   self.requires('googleapis)
        pass


    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = False

        self._cmake.definitions["GOOGLE_CLOUD_CPP_ENABLE_MACOS_OPENSSL_CHECK"] = False

        self._cmake.definitions["GOOGLE_CLOUD_CPP_ENABLE_BIGTABLE"] = True
        self._cmake.definitions["GOOGLE_CLOUD_CPP_ENABLE_BIGQUERY"] = True
        self._cmake.definitions["GOOGLE_CLOUD_CPP_ENABLE_SPANNER"] = True
        self._cmake.definitions["GOOGLE_CLOUD_CPP_ENABLE_STORAGE"] = True
        self._cmake.definitions["GOOGLE_CLOUD_CPP_ENABLE_FIRESTORE"] = True
        self._cmake.definitions["GOOGLE_CLOUD_CPP_ENABLE_PUBSUB"] = True
        self._cmake.definitions["GOOGLE_CLOUD_CPP_ENABLE_IAM"] = True
        self._cmake.definitions["GOOGLE_CLOUD_CPP_ENABLE_LOGGING"] = True
        self._cmake.definitions["GOOGLE_CLOUD_CPP_ENABLE_GENERATOR"] = True

        self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        #tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        pass
