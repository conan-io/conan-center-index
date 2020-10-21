--- CMakeLists.txt
+++ CMakeLists.txt
@@ -3,7 +3,9 @@
 cmake_minimum_required(VERSION 2.6)

 set(VERSION "0.4.9")
-set(datadir ${CMAKE_INSTALL_PREFIX}/share)
+if(NOT datadir)
+  set(datadir ${CMAKE_INSTALL_PREFIX}/share)
+endif()
 set(pkgdatadir ${datadir}/poppler)

 set(unicode-map-files
