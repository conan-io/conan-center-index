#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

#include <stdint.h>

#define configUSE_PREEMPTION @use_preemption@
#define configUSE_PORT_OPTIMISED_TASK_SELECTION @use_port_optimised_task_selection@
#define configUSE_TICKLESS_IDLE @use_tickless_idle@
#define configCPU_CLOCK_HZ @cpu_clock_hz@
#define configSYSTICK_CLOCK_HZ @systick_clock_hz@
#define configTICK_RATE_HZ @tick_rate_hz@
#define configMAX_PRIORITIES @max_priorities@
#define configMINIMAL_STACK_SIZE @minimal_stack_size@
#define configMAX_TASK_NAME_LEN @max_task_name_len@
#define configTICK_TYPE_WIDTH_IN_BITS @tick_type_width_in_bits@
#define configIDLE_SHOULD_YIELD @idle_should_yield@
#define configUSE_TASK_NOTIFICATIONS @use_task_notifications@
#define configTASK_NOTIFICATION_ARRAY_ENTRIES @task_notification_array_entries@
#define configUSE_MUTEXES @use_mutexes@
#define configUSE_RECURSIVE_MUTEXES @use_recursive_mutexes@
#define configUSE_COUNTING_SEMAPHORES @use_counting_semaphores@
#define configQUEUE_REGISTRY_SIZE @queue_registry_size@
#define configUSE_QUEUE_SETS @use_queue_sets@
#define configUSE_TIME_SLICING @use_time_slicing@
#define configUSE_NEWLIB_REENTRANT @use_newlib_reentrant@
#define configENABLE_BACKWARD_COMPATIBILITY @enable_backward_compatibility@
#define configNUM_THREAD_LOCAL_STORAGE_POINTERS @num_thread_local_storage_pointers@
#define configUSE_MINI_LIST_ITEM @use_mini_list_item@
#define configSTACK_DEPTH_TYPE @stack_depth_type@
#define configMESSAGE_BUFFER_LENGTH_TYPE @message_buffer_length_type@
#define configHEAP_CLEAR_MEMORY_ON_FREE @heap_clear_memory_on_free@

/* Memory allocation related definitions. */
#define configSUPPORT_STATIC_ALLOCATION @support_static_allocation@
#define configSUPPORT_DYNAMIC_ALLOCATION @support_dynamic_allocation@
#define configTOTAL_HEAP_SIZE @total_heap_size@
#define configAPPLICATION_ALLOCATED_HEAP @application_allocated_heap@
#define configSTACK_ALLOCATION_FROM_SEPARATE_HEAP @stack_allocation_from_separate_heap@

/* Hook function related definitions. */
#define configUSE_IDLE_HOOK @use_idle_hook@
#define configUSE_TICK_HOOK @use_tick_hook@
#define configCHECK_FOR_STACK_OVERFLOW @check_for_stack_overflow@
#define configUSE_MALLOC_FAILED_HOOK @use_malloc_failed_hook@
#define configUSE_DAEMON_TASK_STARTUP_HOOK @use_daemon_task_startup_hook@
#define configUSE_SB_COMPLETED_CALLBACK @use_sb_completed_callback@

/* Run time and task stats gathering related definitions. */
#define configGENERATE_RUN_TIME_STATS @generate_run_time_stats@
#define configUSE_TRACE_FACILITY @use_trace_facility@
#define configUSE_STATS_FORMATTING_FUNCTIONS @use_stats_formatting_functions@

/* Co-routine related definitions. */
#define configUSE_CO_ROUTINES @use_co_routines@
#define configMAX_CO_ROUTINE_PRIORITIES @max_co_routine_priorities@

/* Software timer related definitions. */
#define configUSE_TIMERS @use_timers@
#define configTIMER_TASK_PRIORITY @timer_task_priority@
#define configTIMER_QUEUE_LENGTH @timer_queue_length@
#define configTIMER_TASK_STACK_DEPTH @timer_task_stack_depth@

/* Interrupt nesting behaviour configuration. */
#define configKERNEL_INTERRUPT_PRIORITY @kernel_interrupt_priority@
#define configMAX_SYSCALL_INTERRUPT_PRIORITY @max_syscall_interrupt_priority@
#define configMAX_API_CALL_INTERRUPT_PRIORITY @max_api_call_interrupt_priority@

/* Define to trap errors during development. */
// #define configASSERT@assert@

/* FreeRTOS MPU specific definitions. */
#define configINCLUDE_APPLICATION_DEFINED_PRIVILEGED_FUNCTIONS @include_application_defined_privileged_functions@
#define configTOTAL_MPU_REGIONS @total_mpu_regions@
#define configTEX_S_C_B_FLASH @tex_s_c_b_flash@
#define configTEX_S_C_B_SRAM @tex_s_c_b_sram@
#define configENFORCE_SYSTEM_CALLS_FROM_KERNEL_ONLY @enforce_system_calls_from_kernel_only@
#define configALLOW_UNPRIVILEGED_CRITICAL_SECTIONS @allow_unprivileged_critical_sections@
#define configENABLE_ERRATA_837070_WORKAROUND @enable_errata_837070_workaround@
#define configUSE_MPU_WRAPPERS_V1 @use_mpu_wrappers_v1@
#define configPROTECTED_KERNEL_OBJECT_POOL_SIZE @protected_kernel_object_pool_size@
#define configSYSTEM_CALL_STACK_SIZE @system_call_stack_size@

/* ARMv8-M secure side port related definitions. */
#define secureconfigMAX_SECURE_CONTEXTS @max_secure_contexts@

/* Optional functions - most linkers will remove unused functions anyway. */
#define INCLUDE_vTaskPrioritySet @include_vTaskPrioritySet@
#define INCLUDE_uxTaskPriorityGet @include_uxTaskPriorityGet@
#define INCLUDE_vTaskDelete @include_vTaskDelete@
#define INCLUDE_vTaskSuspend @include_vTaskSuspend@
#define INCLUDE_xResumeFromISR @include_xResumeFromISR@
#define INCLUDE_vTaskDelayUntil @include_vTaskDelayUntil@
#define INCLUDE_vTaskDelay @include_vTaskDelay@
#define INCLUDE_xTaskGetSchedulerState @include_xTaskGetSchedulerState@
#define INCLUDE_xTaskGetCurrentTaskHandle @include_xTaskGetCurrentTaskHandle@
#define INCLUDE_uxTaskGetStackHighWaterMark @include_uxTaskGetStackHighWaterMark@
#define INCLUDE_uxTaskGetStackHighWaterMark2 @include_uxTaskGetStackHighWaterMark2@
#define INCLUDE_xTaskGetIdleTaskHandle @include_xTaskGetIdleTaskHandle@
#define INCLUDE_eTaskGetState @include_eTaskGetState@
#define INCLUDE_xEventGroupSetBitFromISR @include_xEventGroupSetBitFromISR@
#define INCLUDE_xTimerPendFunctionCall @include_xTimerPendFunctionCall@
#define INCLUDE_xTaskAbortDelay @include_xTaskAbortDelay@
#define INCLUDE_xTaskGetHandle @include_xTaskGetHandle@
#define INCLUDE_xTaskResumeFromISR @include_xTaskResumeFromISR@

#endif /* FREERTOS_CONFIG_H */
