--- CMakeLists.txt
+++ CMakeLists.txt
@@ -86,12 +86,12 @@
         if (USE_OPENSSL AND NOT ANDROID)
             find_package(OpenSSL REQUIRED)
             find_package(Threads REQUIRED)
-            add_library(crypto UNKNOWN IMPORTED)
+            add_library(crypto INTERFACE IMPORTED)
             set_target_properties(crypto PROPERTIES
                 INTERFACE_INCLUDE_DIRECTORIES "${OPENSSL_INCLUDE_DIR}")
             set_target_properties(crypto PROPERTIES
-                IMPORTED_LINK_INTERFACE_LANGUAGES "C"
-                IMPORTED_LOCATION "${OPENSSL_CRYPTO_LIBRARY}")
+                #IMPORTED_LINK_INTERFACE_LANGUAGES "C"
+                INTERFACE_LINK_LIBRARIES "OpenSSL::Crypto")
             add_dependencies(crypto Threads::Threads)
             message(STATUS "Using libcrypto from system: ${OPENSSL_CRYPTO_LIBRARY}")
         elseif(NOT USE_OPENSSL AND IN_SOURCE_BUILD)

