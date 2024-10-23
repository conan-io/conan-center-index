#include <libv4l2.h>
#include <fcntl.h>

int main() {
    v4l2_open("test", O_RDWR);
}
