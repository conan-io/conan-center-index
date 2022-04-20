from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class CaffeConan(ConanFile):
    name = "caffe"
    description = "Caffe: a fast open framework for deep learning"
    topics = ("conan", "caffe", "deep-learning", "machine-learning")
    url = "https://github.com/bincrafters/conan-caffe"
    homepage = "http://caffe.berkeleyvision.org"
    license = "BSD-2-Clause"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"

    settings = "os", "arch", "compiler", "build_type"

    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_gpu": [True, False],
               "with_cudnn": [True, False],
               "with_opencv": [True, False],
               "with_leveldb": [True, False],
               "with_lmdb": [True, False],
               "gpu_arch": ["Fermi", "Kepler", "Maxwell", "Pascal", "All", "Manual"],
               # following options are valid when gpu_arch=Manual
               "gpu_arch_bin": "ANY",
               "gpu_arch_ptx": "ANY"
               }
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_gpu": False,
                       "with_cudnn": False,
                       "with_opencv": False,
                       "with_leveldb": False,
                       "with_lmdb": False,
                       # this default ensures build with modern CUDA that omit Fermi
                       "gpu_arch": "Kepler",
                       "gpu_arch_bin": "",
                       "gpu_arch_ptx": ""
                       }

    @property
    def original_version(self):
        if 'dssl' in self.version:
            v = self.version.split('.')
            return '.'.join(v[:-1])
        return self.version

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if not self.options.with_gpu:
            del self.options.gpu_arch
            del self.options.gpu_arch_bin
            del self.options.gpu_arch_ptx

    def requirements(self):
        self.requires.add("boost/1.69.0.dssl1")
        self.requires.add("glog/0.4.0")
        self.requires.add("gflags/2.2.2")
        self.requires.add("hdf5/1.10.6")
        # caffe supports those BLAS implementations: openblas, mkl, accelerate, atlas
        # Choose Accelerate for MAC and openblas otherwise
        if self.settings.os != "Macos":
            self.requires.add("openblas/0.3.7.dssl1")
        self.requires.add("protobuf/3.9.1.dssl2")
        if self.options.with_opencv:
            self.requires.add("opencv/2.4.13.7")
        if self.options.with_leveldb:
            self.requires.add("leveldb/1.22")
        if self.options.with_lmdb:
            self.requires.add("lmdb/0.9.28.dssl1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.original_version])
        extracted_dir = self.name + "-" + os.path.basename(self.conan_data["sources"][self.original_version].get("url")).split(".tar.gz")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self, generator='Ninja', parallel=False)
        cmake.definitions["BUILD_python"] = False
        cmake.definitions["BUILD_python_layer"] = False
        cmake.definitions["BUILD_docs"] = False

        cmake.definitions["CPU_ONLY"] = not self.options.with_gpu
        cmake.definitions["USE_OPENCV"] = self.options.with_opencv
        cmake.definitions["USE_LEVELDB"] = self.options.with_leveldb
        cmake.definitions["USE_LMDB"] = self.options.with_lmdb
        cmake.definitions["USE_CUDNN"] = self.options.with_cudnn

        if self.settings.os == "Windows":
            cmake.definitions["USE_PREBUILT_DEPENDENCIES"] = False
            cmake.definitions["COPY_PREREQUISITES"] = False
            cmake.definitions["INSTALL_PREREQUISITES"] = False

        protoc = "protoc.exe" if self.settings.os == "Windows" else "protoc"
        cmake.definitions["PROTOBUF_PROTOC_EXECUTABLE"] = os.path.join(self.deps_cpp_info['protobuf'].rootpath, 'bin', protoc)

        if self.options.with_gpu:
            cmake.definitions["CUDA_ARCH_NAME"] = self.options.gpu_arch
            if self.options.gpu_arch == "Manual":
                cmake.definitions["CUDA_ARCH_BIN"] = self.options.gpu_arch_bin
                cmake.definitions["CUDA_ARCH_PTX"] = self.options.gpu_arch_ptx
            cmake.definitions["CUDA_NVCC_FLAGS"] = '-std=c++11'

        cmake.definitions["BLAS"] = "open"

        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _prepare(self):
        # ensure that bundled cmake files are not used
        for module in ['Glog', 'GFlags', 'OpenBLAS']:
            os.unlink(os.path.join(self._source_subfolder, 'cmake', 'Modules', 'Find'+module+'.cmake'))
        # drop autogenerated CMake files for protobuf because they prevent
        # `cmake/ProtoBuf.cmake` to detect Protobuf using system FindProtobuf
        for module in ['protobuf', 'protoc']:
            if os.path.exists('Find'+module+'.cmake'):
                os.unlink('Find'+module+'.cmake')
        # patch sources
        if self.conan_data["patches"].get(self.original_version):
            for patch in self.conan_data["patches"][self.original_version]:
                tools.patch(**patch)

    def build(self):
        self._prepare()
        cmake = self._configure_cmake()
        cmake.build(target='caffe')
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        # remove python bindings
        tools.rmdir(os.path.join(self.package_folder, 'python'))
        # remove cmake
        tools.rmdir(os.path.join(self.package_folder, 'share'))

    def package_info(self):
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                self.cpp_info.libs = ["caffe-d", "caffeproto-d"]
            else:
                self.cpp_info.libs = ["caffe", "caffeproto"]
            self.cpp_info.bindirs = ['bin', 'lib']
        else:
            if self.settings.build_type == "Debug":
                self.cpp_info.libs = ["caffe-d", "proto-d"]
            else:
                self.cpp_info.libs = ["caffe", "proto"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]

        # pass options from Caffe_DEFINITIONS
        if not self.options.with_gpu:
            self.cpp_info.defines.append("CPU_ONLY")
        if self.options.with_opencv:
            self.cpp_info.defines.append("USE_OPENCV")
        if self.options.with_leveldb:
            self.cpp_info.defines.append("USE_LEVELDB")
        if self.options.with_lmdb:
            self.cpp_info.defines.append("USE_LMDB")
        if self.options.with_cudnn:
            self.cpp_info.defines.append("USE_CUDNN")
        if self.settings.os == "Macos":
            # not for all cases but usually works
            self.cpp_info.defines.append("USE_ACCELERATE")

        # fix export names
        self.cpp_info.names["cmake_find_package"] = "Caffe"
        self.cpp_info.names["cmake_find_package_multi"] = "Caffe"
