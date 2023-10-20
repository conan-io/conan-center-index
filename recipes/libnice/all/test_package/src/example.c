#include <nice/agent.h>

int main()
{
    NiceAgent *agent = nice_agent_new(NULL, NICE_COMPATIBILITY_RFC5245);
    g_object_unref(agent);
}
