--- 3fd/core/preprocessing.h
+++ 3fd/core/preprocessing.h
@@ -66,7 +66,7 @@
 #    define _newLine_ "\r\n"
 #    define dbg_new new

-#elif defined __unix__ // Unix only:
+#elif defined(__unix__) || defined(__APPLE__)
 #    define _3FD_POCO_SUPPORT
 #    define _3FD_CONSOLE_AVAILABLE
 #    define _newLine_ "\r\n"
