#include "cwt-cucumber/cucumber.hpp"


CUSTOM_PARAMETER(custom_event, "{event}", R"('(.*?)')", "a custom event") {
  std::string event = CUKE_PARAM_ARG(1);
  return event;
}
