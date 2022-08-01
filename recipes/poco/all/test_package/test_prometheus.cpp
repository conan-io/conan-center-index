#include "Poco/Prometheus/MetricsServer.h"
#include "Poco/Prometheus/ProcessCollector.h"
#include "Poco/Prometheus/ThreadPoolCollector.h"

using Poco::Prometheus::MetricsServer;
using Poco::Prometheus::ProcessCollector;
using Poco::Prometheus::ThreadPoolCollector;

int main() {
  ProcessCollector pc;
  ThreadPoolCollector collectorForDefaultThreadPool();

  const Poco::UInt16 metricsPort = 9177; // hope this does not clash
	MetricsServer server(metricsPort);
	server.start();

	// Don't wait for TerminationRequest and stop immediately (This is a test server)
	//waitForTerminationRequest();

  server.stop();
}
