/*
 * check_events.c - show event encoding
 *
 * Copyright (c) 2009 Google, Inc
 * Contributed by Stephane Eranian <eranian@gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 * PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 * CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
 * OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 * This file is part of libpfm, a performance monitoring support library for
 * applications on Linux.
 */
#include <sys/types.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <perfmon/err.h>

#include <perfmon/pfmlib.h>

int
pmu_is_present(pfm_pmu_t p)
{
	pfm_pmu_info_t pinfo;
	int ret;

	memset(&pinfo, 0, sizeof(pinfo));
	ret = pfm_get_pmu_info(p, &pinfo);
	return ret == PFM_SUCCESS ? pinfo.is_present : 0;
}

int
main(int argc, const char **argv)
{
	pfm_pmu_info_t pinfo;
	pfm_pmu_encode_arg_t e;
	const char *arg[3];
	const char **p;
	char *fqstr;
	pfm_event_info_t info;
	int j, ret;
	int i;
	int total_supported_events = 0;
	int total_available_events = 0;

	/*
	 * Initialize pfm library (required before we can use it)
	 */
	ret = pfm_initialize();
	if (ret != PFM_SUCCESS)
		errx(1, "cannot initialize library: %s\n", pfm_strerror(ret));

	memset(&pinfo, 0, sizeof(pinfo));
	memset(&info, 0, sizeof(info));

	printf("Supported PMU models:\n");
	for(i=PFM_PMU_NONE; i < PFM_PMU_MAX; i++) {
		auto pmu = static_cast<pfm_pmu_t>(i);
		ret = pfm_get_pmu_info(pmu, &pinfo);
		if (ret != PFM_SUCCESS)
			continue;

		printf("\t[%d, %s, \"%s\"]\n", i, pinfo.name, pinfo.desc);
	}

	printf("Detected PMU models:\n");
	for(i=PFM_PMU_NONE; i < PFM_PMU_MAX; i++) {
		auto pmu = static_cast<pfm_pmu_t>(i);
		ret = pfm_get_pmu_info(pmu, &pinfo);
		if (ret != PFM_SUCCESS)
			continue;
		if (pinfo.is_present) {
			printf("\t[%d, %s, \"%s\"]\n", i, pinfo.name, pinfo.desc);
			total_supported_events += pinfo.nevents;
		}
		total_available_events += pinfo.nevents;
	}

	printf("Total events: %d available, %d supported\n", total_available_events, total_supported_events);

	return 0;

	/*
	 * be nice to user!
	 */
	if (argc < 2  && pmu_is_present(PFM_PMU_PERF_EVENT)) {
		arg[0] = "PERF_COUNT_HW_CPU_CYCLES";
		arg[1] = "PERF_COUNT_HW_INSTRUCTIONS";
		arg[2] = NULL;
		p = arg;
	} else {
		p = argv+1;
	}

	if (!*p)
		errx(1, "you must pass at least one event");

	memset(&e, 0, sizeof(e));
	while(*p) {
		/*
		 * extract raw event encoding
		 *
		 * For perf_event encoding, use
		 * #include <perfmon/pfmlib_perf_event.h>
		 * and the function:
		 * pfm_get_perf_event_encoding()
		 */
		fqstr = NULL;
		e.fstr = &fqstr;
		ret = pfm_get_os_event_encoding(*p, PFM_PLM0|PFM_PLM3, PFM_OS_NONE, &e);
		if (ret != PFM_SUCCESS) {
			/*
			 * codes is too small for this event
			 * free and let the library resize
			 */
			if (ret == PFM_ERR_TOOSMALL) {
				free(e.codes);
				e.codes = NULL;
				e.count = 0;
				free(fqstr);
				continue;
			}
			if (ret == PFM_ERR_NOTFOUND && strstr(*p, "::"))
				errx(1, "%s: try setting LIBPFM_ENCODE_INACTIVE=1", pfm_strerror(ret));
			errx(1, "cannot encode event %s: %s", *p, pfm_strerror(ret));
		}
		ret = pfm_get_event_info(e.idx, PFM_OS_NONE, &info);
		if (ret != PFM_SUCCESS)
			errx(1, "cannot get event info: %s", pfm_strerror(ret));

		ret = pfm_get_pmu_info(info.pmu, &pinfo);
		if (ret != PFM_SUCCESS)
			errx(1, "cannot get PMU info: %s", pfm_strerror(ret));

		printf("Requested Event: %s\n", *p);
		printf("Actual    Event: %s\n", fqstr);
		printf("PMU            : %s\n", pinfo.desc);
		printf("IDX            : %d\n", e.idx);
		printf("Codes          :");
		for(j=0; j < e.count; j++)
			printf(" 0x%"PRIx64, e.codes[j]);
		putchar('\n');

		free(fqstr);
		p++;
	}
	if (e.codes)
		free(e.codes);
	return 0;
}
