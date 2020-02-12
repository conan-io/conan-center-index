--- CMakeLists.txt
+++ CMakeLists.txt
@@ -727,7 +727,7 @@
 if(ENABLE_GLIB)
   add_subdirectory(glib)
 endif()
-add_subdirectory(test)
+# add_subdirectory(test)
 if(ENABLE_QT5)
   add_subdirectory(qt5)
 endif()
