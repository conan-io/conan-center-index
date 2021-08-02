diff --git a/CMakeLists.txt b/CMakeLists.txt
index b72effbe..0d77dd63 100644
--- a/CMakeLists.txt
+++ b/CMakeLists.txt
@@ -16,8 +16,6 @@ option(S2N_NO_PQ "Disables all Post Quantum Crypto code. You likely want this
 for older compilers or uncommon platforms." OFF)
 option(S2N_NO_PQ_ASM "Turns off the ASM for PQ Crypto even if it's available for the toolchain.
 You likely want this on older compilers." OFF)
-option(SEARCH_LIBCRYPTO "Set this if you want to let S2N search libcrypto for you,
-otherwise a crypto target needs to be defined." ON)
 option(UNSAFE_TREAT_WARNINGS_AS_ERRORS "Compiler warnings are treated as errors. Warnings may
 indicate danger points where you should verify with the S2N-TLS developers that the security of
 the library is not compromised. Turn this OFF to ignore warnings." ON)
@@ -342,15 +340,12 @@ endif()
 
 set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake/modules)
 
-if (SEARCH_LIBCRYPTO)
-    find_package(LibCrypto REQUIRED)
-else()
-    if (TARGET crypto)
-        message(STATUS "S2N found target: crypto")
-    else()
-        message(FATAL_ERROR "Target crypto is not defined, failed to find libcrypto")
-    endif()
-endif()
+find_package(OpenSSL REQUIRED)
+add_library(crypto INTERFACE IMPORTED)
+set_target_properties(crypto PROPERTIES
+  INTERFACE_INCLUDE_DIRECTORIES "${OPENSSL_INCLUDE_DIR}")
+set_target_properties(crypto PROPERTIES
+  INTERFACE_LINK_LIBRARIES "OpenSSL::Crypto")
 target_link_libraries(${PROJECT_NAME} PUBLIC crypto ${OS_LIBS} m)
 
 target_include_directories(${PROJECT_NAME} PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>)
