from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import collect_libs, get, apply_conandata_patches, export_conandata_patches, copy
from conan.errors import ConanException
import os
import shutil
import platform
import re
import warnings

class SuitesparseConan(ConanFile):
    name = "suitesparse"
    license = "SPEX"
    url = "https://github.com/DrTimothyAldenDavis/SuiteSparse"
    description = "SuiteSparse: A Suite of Sparse matrix packages at https://github.com/DrTimothyAldenDavis/SuiteSparse"
    homepage = "https://github.com/DrTimothyAldenDavis/SuiteSparse"
    topics = ("suitesparse", "sparse", "linear-algebra", "numerical", "matrix", "graph", "umfpack", "cholmod", "spqr", "btf", "amd", "colamd", "camd", "klu", "util", "cuda", "gpu")
    package_type = "library"   
    settings = "os", "arch", "compiler", "build_type"  
    options = {
        "shared": [True, False], 
        "cuda_archs": [None, "ANY"], # Example: 50;75;80 min. 50
        "use_cuda": [True, False],
        "blas_vendor": [None, "ANY"],
        "use_fortran": [True, False],
        "use_blascpp": [True, False],
        "use_lapackcpp": [True, False],
        "build_testing": [True, False]
    } 
    default_options = {
        "shared": True, 
        "cuda_archs": None,
        "use_cuda": False,
        "use_fortran": False,
        "use_blascpp": False,
        "use_lapackcpp": False,
        "build_testing": False,
        "blas_vendor": "conan-OpenBLAS" # Please add path to CMAKE_PREFIX_PATH using env if you use external blas implementation library such like as OpenBLAS. See https://cmake.org/cmake/help/latest/module/FindBLAS.html
    }    
    requires = [
        "gmp/[>=6.3.0 <7]",
        "mpfr/[>=4.2.1 <5]",    
    ]   
    intel_bla_vendors = ["Intel", "Intel10_32","Intel10_64lp", "Intel10_64lp_seq", "Intel10_64ilp", "Intel10_64ilp_seq", "Intel10_64_dyn"]
    use_intel_mkl = False
                
    @property          
    def intel_mkl_path(self):
        return os.environ.get("MKLROOT", None)
        
    def validate_cuda_archs(self):
        raw = self.options.cuda_archs
        if raw is None:
            raise ConanException("“The cuda_archs option must be set when the use_cuda option is enabled.")  
        items = raw if isinstance(raw, (list, tuple)) else str(raw).split(";")
        try:
            vals = [int(x) for x in items]
        except ValueError:
            raise ConanException(f"Bad format: cuda_archs={raw}")
        if not vals or any(v < 50 for v in vals):
            raise ConanException(f"cuda_archs must be integer(s) > 50, got {vals}")
        
    def validate(self):
        if self.options.use_cuda:
            self.validate_cuda_archs()
  
    def requirements(self): 
        # OpenBLAS from conan center package
        if self.options.blas_vendor == 'conan-OpenBLAS':
            if self.settings.os in ["Windows"]:
                raise ConanException("OpenBLAS from conan center is not supported on Windows. Try using Intel MKL and set BLA_VENDOR eg. Intel10_64ilp_seq")       
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.requires("gfortran/[>=10.2]")
                self.requires("openblas/[>=0.3.27 <1]")
                
        # OpenBLAS from intel MKL
        self.use_intel_mkl = self.options.blas_vendor in self.intel_bla_vendors                       
        if self.use_intel_mkl and not self.intel_mkl_path:
            raise ConanException("Not found MKLROOT enviromment path. MKLROOT is required to obtain OpenBLAS library directory.")
        elif self.intel_mkl_path:
            self.output.info(f"Found Intel MKL at: {self.intel_mkl_path}")
              
    def layout(self):
        cmake_layout(self, src_folder="src")
        
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)  
        
    def export_sources(self):
        export_conandata_patches(self)
        
    def generate(self):
        deps = CMakeDeps(self)
        deps.set_property("gmp", "cmake_file_name", "GMP")
        deps.set_property("gmp", "cmake_target_name", "GMP::GMP")
        deps.set_property("mpfr", "cmake_file_name", "MPFR")
        deps.set_property("mpfr", "cmake_target_name", "MPFR::MPFR")
        
        deps.generate()
        tc = CMakeToolchain(self)
             
        # CUDA:
        tc.variables["SUITESPARSE_USE_CUDA"] = self.options.use_cuda
        tc.variables["SUITESPARSE_CUDA_ARCHITECTURES"] = self.options.cuda_archs
        
        # OpenBLAS from conan center:
        if self.options.blas_vendor == 'conan-OpenBLAS':
            libdirs = self.dependencies["openblas"].cpp_info.libdirs       
            openblas_lib = next((
                os.path.join(root, file).replace("\\", "/")
                for libdir in libdirs
                for root, dirs, files in os.walk(libdir)
                for file in files
                if "openblas" in file.lower() and file.endswith(('.a', '.so', '.lib'))
            ), "")
                   
            tc.variables["BLAS_LIBRARIES"] = openblas_lib
            tc.variables["LAPACK_LIBRARIES"] = openblas_lib
            tc.variables["BLA_VENDOR"] = 'OpenBLAS'
            
        # Other BLAS implementation:
        else:
            tc.variables["BLA_VENDOR"] = self.options.blas_vendor
            
        # Others:
        tc.blocks.remove("vs_runtime") # fix msvc bug
        tc.variables["BUILD_TESTING"] = self.options.build_testing
        
        # Other dependencies:
        tc.variables["SUITESPARSE_USE_FORTRAN"] = self.options.use_fortran
        tc.variables["BLAS++"] = self.options.use_blascpp
        tc.variables["LAPACK++"] = self.options.use_lapackcpp  
        
        tc.generate()

    def build(self):    
        apply_conandata_patches(self)
        
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt",
         dst=os.path.join(self.package_folder, "licenses"),
         src=self.source_folder)
    
        cmake = CMake(self)
        cmake.install()

        
    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SuiteSparse")
        self.cpp_info.set_property("cmake_target_name", "SuiteSparse::SuiteSparse")
        self.cpp_info.set_property("pkg_config_name", "SuiteSparse")
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.bindirs = ["bin"]            
       
        if self.use_intel_mkl:
            intel_bindir = os.path.join(str(self.intel_mkl_path), "bin").replace("\\", "/")
            intel_libdir = os.path.join(str(self.intel_mkl_path), "bin").replace("\\", "/")
        
            self.cpp_info.bindirs.append(intel_bindir)
            self.cpp_info.libdirs.append(intel_libdir)
        