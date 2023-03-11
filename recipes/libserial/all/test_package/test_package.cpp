#include <cstdlib>

#include <libserial/SerialPort.h>
#include <libserial/SerialStream.h>

int main(void) {
    using LibSerial::SerialPort ;
    using LibSerial::SerialStream ;

    // Instantiate a Serial Port and a Serial Stream object.
    SerialPort serial_port ;
    SerialStream serial_stream ;

    serial_port.IsOpen();
    serial_stream.IsOpen();

    return EXIT_SUCCESS;
}
