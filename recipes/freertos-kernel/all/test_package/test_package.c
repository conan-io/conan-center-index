#include <stdint.h>

#include <FreeRTOS.h>
#include <semphr.h>

volatile uint32_t task_status_ticks = 0;

void vApplicationTickHook( void ) { return; }

void vApplicationMallocFailedHook( void ) {
    for ( ;; ) {}
}

void vApplicationIdleHook(void) {}

void vApplicationDaemonTaskStartupHook( void ) {}

//==============================================================================
void HardFault_Handler( void )
{
    for ( ;; ) {}
}

//==============================================================================
int main()
{
    SemaphoreHandle_t semPtr = xSemaphoreCreateBinary();
    return 0;
}
