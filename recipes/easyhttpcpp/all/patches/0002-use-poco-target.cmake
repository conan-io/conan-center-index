--- CMakeLists.txt
+++ CMakeLists.txt
@@ -110,7 +110,7 @@
                       )

 target_link_libraries(${LIBRARY_TARGET_NAME}
-	              ${Poco_LIBRARIES}
+	              Poco::Poco
                       ${OPENSSL_SSL_LIBRARY}
                       ${OPENSSL_CRYPTO_LIBRARY})

