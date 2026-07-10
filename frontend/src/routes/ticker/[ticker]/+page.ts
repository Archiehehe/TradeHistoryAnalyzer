import { error } from '@sveltejs/kit';

import { getTickerReport } from '$lib/api';

export const load = async ({ fetch, params, url }) => {
  const reportId = url.searchParams.get('reportId');
  if (!reportId) {
    throw error(400, 'A reportId query parameter is required for ticker detail pages.');
  }

  const tickerReport = await getTickerReport(fetch, reportId, params.ticker);
  return {
    reportId,
    tickerReport
  };
};

