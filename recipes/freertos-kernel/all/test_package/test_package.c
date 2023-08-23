#include <stdint.h>

#include <freertos-kernel/FreeRTOS.h>
#include <freertos-kernel/semphr.h>

volatile uint32_t task_status_ticks = 0;

//==============================================================================
extern void vApplicationTickHook( void ) { return; }

//==============================================================================
extern void vApplicationMallocFailedHook( void )
{
    taskDISABLE_INTERRUPTS();
    for ( ;; )
    {
    }
}

//==============================================================================
extern void vApplicationIdleHook( void )
{
}

//==============================================================================
extern void vApplicationStackOverflowHook( TaskHandle_t pxTask,
                                               char *pcTaskName )
{
    (void)pcTaskName;
    (void)pxTask;
    taskDISABLE_INTERRUPTS();
    for ( ;; )
    {
    }
}

//==============================================================================
extern void HardFault_Handler( void )
{
    for ( ;; )
    {
    }
}

//==============================================================================
int main()
{
    SemaphoreHandle_t semPtr = xSemaphoreCreateBinary();
    return 0;
}
