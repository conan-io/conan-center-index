#include <cjson/cJSON.h>

#include <stdio.h>
#include <stdlib.h>

char *create_monitor_with_helpers() {
  const unsigned int resolution_numbers[3][2] = {
    {1280, 720},
    {1920, 1080},
    {3840, 2160}
  };
  char *string = NULL;
  cJSON *resolutions = NULL;
  size_t index = 0;

  cJSON *monitor = cJSON_CreateObject();

  if (cJSON_AddStringToObject(monitor, "name", "Awesome 4K") == NULL) {
    goto end;
  }

  resolutions = cJSON_AddArrayToObject(monitor, "resolutions");
  if (resolutions == NULL) {
    goto end;
  }

  for (index = 0; index < (sizeof(resolution_numbers) / (2 * sizeof(int))); ++index) {
    cJSON *resolution = cJSON_CreateObject();

    if (cJSON_AddNumberToObject(resolution, "width", resolution_numbers[index][0]) == NULL) {
      goto end;
    }

    if (cJSON_AddNumberToObject(resolution, "height", resolution_numbers[index][1]) == NULL) {
      goto end;
    }

    cJSON_AddItemToArray(resolutions, resolution);
  }

  string = cJSON_Print(monitor);
  if (string == NULL) {
    fprintf(stderr, "Failed to print monitor.\n");
  }

end:
  cJSON_Delete(monitor);
  return string;
}

int main() {
  char *json = create_monitor_with_helpers();
  printf("%s\n", json);
  free(json);

  return 0;
}
