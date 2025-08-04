from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import get, copy, rmdir
from conan.errors import ConanInvalidConfiguration
from os.path import join

required_conan_version = ">=2.4"


class kubernetesRecipe(ConanFile):
    name = "kubernetes"
    package_type = "library"

    # Optional metadata
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kubernetes-client/c"
    description = "Official C client library for Kubernetes"
    topics = ("kubernetes", "k8s", "kubernetes-client", "k8s-client")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}

    implements = ["auto_shared_fpic", "auto_language"]
    languages = "C"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        if self.settings.compiler == "msvc":
            raise ConanInvalidConfiguration(f"{self.ref} can not be used on msvc.")

    def requirements(self):
        self.requires("libcurl/[>=7.78.0 <9]", transitive_headers=True)
        self.requires("openssl/[>=1.1 <4]")
        self.requires("libwebsockets/4.3.2", transitive_headers=True)
        self.requires("libyaml/0.2.5")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="kubernetes")
        cmake.build()

    def package(self):
        copy(self, "*.h", src=join(self.source_folder, "kubernetes", "api"), dst=join(self.package_folder, "include/kubernetes/api"), keep_path=False)
        copy(self, "*.h", src=join(self.source_folder, "kubernetes", "model"), dst=join(self.package_folder, "include/kubernetes/model"), keep_path=False)
        copy(self, "*.h", src=join(self.source_folder, "kubernetes", "config"), dst=join(self.package_folder, "include/kubernetes/config"), keep_path=False)
        copy(self, "*.h", src=join(self.source_folder, "kubernetes", "include"), dst=join(self.package_folder, "include/kubernetes/include"), keep_path=False)
        copy(self, "*.h", src=join(self.source_folder, "kubernetes", "websocket"), dst=join(self.package_folder, "include/kubernetes/websocket"), keep_path=False)
        copy(self, "*.h", src=join(self.source_folder, "kubernetes", "external"), dst=join(self.package_folder, "include/kubernetes/external"), keep_path=False)
        copy(self, "*.h", src=join(self.source_folder, "kubernetes", "watch"), dst=join(self.package_folder, "include/kubernetes/watch"), keep_path=False)
        copy(self, "LICENSE", src=join(self.source_folder), dst=join(self.package_folder, "licenses"), keep_path=False)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["kubernetes"]
