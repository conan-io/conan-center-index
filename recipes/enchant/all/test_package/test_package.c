#include <enchant.h>
#include <stddef.h>
#include <stdio.h>

static void for_each_provider(const char* const provider_name,
                              const char* const provider_desc,
                              const char* const provider_dll_file,
                              void* user_data)
{
  (void)provider_desc;
  (void)provider_dll_file;

  ++*(int*)user_data;
  (void)puts(provider_name);
}

int main(void)
{
  EnchantBroker* broker = enchant_broker_init();
  char* prefix_dir = NULL;
  int counter = 0;
  int return_code = 0;

  if (broker == NULL) {
    (void)fputs("Failed to init the broker", stderr);
    return 1;
  }

  (void)puts("Providers found:");
  enchant_broker_describe(broker, for_each_provider, &counter);
  if (counter == 0) {
    (void)puts("(none)");
  }
  /* NOTE: this is temporary, since the recipe always uses the hunspell
   *       provider */
  if (counter != 1) {
    (void)fflush(stdout);
    (void)fprintf(stderr,
                  "Expected to find exactly 1 provider, found %d\n",
                  counter);
    return_code = 1;
  } else {
    (void)printf("\nenchant version %s\n", enchant_get_version());
  }

  enchant_broker_free(broker);
  return return_code;
}
