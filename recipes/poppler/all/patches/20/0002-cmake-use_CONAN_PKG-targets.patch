--- CMakeLists.txt
+++ CMakeLists.txt
@@ -29,1 +29,1 @@
-find_package (ECM 1.6.0 QUIET NO_MODULE)
+#find_package (ECM 1.6.0 QUIET NO_MODULE)
@@ -204,1 +204,1 @@
-  macro_optional_find_package(Iconv)
+  macro_optional_find_package(Iconv REQUIRED)
@@ -218,1 +218,1 @@
-  find_package(OpenJPEG)
+  find_package(OpenJPEG REQUIRED)
@@ -235,1 +235,1 @@
-  find_package(LCMS2)
+  find_package(LCMS2 REQUIRED)
@@ -241,1 +241,1 @@
-  find_package(CURL)
+  find_package(CURL REQUIRED)
@@ -417,1 +417,1 @@
-set(poppler_LIBS ${FREETYPE_LIBRARIES})
+set(poppler_LIBS CONAN_PKG::freetype)
@@ -439,2 +439,2 @@
-if(FONTCONFIG_FOUND)
+if(WITH_FONTCONFIGURATION_FONTCONFIG)
-  set(poppler_LIBS ${poppler_LIBS} ${FONTCONFIG_LIBRARIES})
+  set(poppler_LIBS ${poppler_LIBS} CONAN_PKG::fontconfig)
@@ -443,5 +443,5 @@if(JPEG_FOUND)
-if(JPEG_FOUND)
+if(ENABLE_JPEG)
   set(poppler_SRCS ${poppler_SRCS}
     poppler/DCTStream.cc
   )
-  set(poppler_LIBS ${poppler_LIBS} ${JPEG_LIBRARIES})
+  set(poppler_LIBS ${poppler_LIBS} CONAN_PKG::libjpeg)
@@ -466,1 +466,1 @@
-    set(poppler_LIBS ${poppler_LIBS} ${CURL_LIBRARIES})
+    set(poppler_LIBS ${poppler_LIBS} CONAN_PKG::libcurl)
@@ -476,4 +476,4 @@
-    set(poppler_LIBS ${poppler_LIBS} ${NSS3_LIBRARIES})
-    include_directories(SYSTEM ${NSS3_INCLUDE_DIRS})
+    set(poppler_LIBS ${poppler_LIBS} CONAN_PKG::nss3)
+    #include_directories(SYSTEM ${NSS3_INCLUDE_DIRS})
   else()
-    set(poppler_LIBS ${poppler_LIBS} PkgConfig::NSS3)
+    set(poppler_LIBS ${poppler_LIBS} CONAN_PKG::nss3)
@@ -482,5 +482,5 @@
-if (OpenJPEG_FOUND)
+if (ENABLE_LIBOPENJPEG STREQUAL "libopenjpeg2")
   set(poppler_SRCS ${poppler_SRCS}
     poppler/JPEG2000Stream.cc
   )
-  set(poppler_LIBS ${poppler_LIBS} openjp2)
+  set(poppler_LIBS ${poppler_LIBS} CONAN_PKG::openjpeg)
@@ -493,1 +493,1 @@
-  set(poppler_LIBS ${poppler_LIBS} ${LCMS2_LIBRARIES})
+  set(poppler_LIBS ${poppler_LIBS} CONAN_PKG::lcms)
--- qt5/src/CMakeLists.txt
+++ qt5/src/CMakeLists.txt
@@ -48,1 +48,1 @@
-target_link_libraries(poppler-qt5 poppler ${Qt5Core_LIBRARIES} ${Qt5Gui_LIBRARIES} ${Qt5Xml_LIBRARIES} ${FREETYPE_LIBRARIES})
+target_link_libraries(poppler-qt5 poppler ${Qt5Core_LIBRARIES} ${Qt5Gui_LIBRARIES} ${Qt5Xml_LIBRARIES} CONAN_PKG::freetype)
--- qt6/src/CMakeLists.txt
+++ qt6/src/CMakeLists.txt
@@ -45,1 +45,1 @@
-target_link_libraries(poppler-qt6 poppler Qt6::Core Qt6::Gui ${FREETYPE_LIBRARIES})
+target_link_libraries(poppler-qt6 poppler Qt6::Core Qt6::Gui CONAN_PKG::freetype)
--- cmake/modules/FindLCMS2.cmake
+++ cmake/modules/FindLCMS2.cmake
@@ -19,5 +19,5 @@
-if(NOT WIN32)
+if(1)
    find_package(PkgConfig)
    pkg_check_modules(PC_LCMS2 lcms2)
    set(LCMS2_DEFINITIONS ${PC_LCMS2_CFLAGS_OTHER})
-endif(NOT WIN32)
+endif()
@@ -32,1 +32,1 @@
-find_library(LCMS2_LIBRARIES NAMES lcms2 liblcms2 lcms-2 liblcms-2
+find_library(LCMS2_LIBRARIES NAMES lcms2 liblcms2 lcms-2 liblcms-2 lcms2_static
