import { getReport, getReportWarnings } from '$lib/api';

export const load = async ({ fetch, params }) => {
  const [report, warnings] = await Promise.all([getReport(fetch, params.reportId), getReportWarnings(fetch, params.reportId)]);

  return {
    report,
    warnings
  };
};

