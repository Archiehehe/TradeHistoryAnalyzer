import { getHealth, getIntegrationStatus } from '$lib/api';
import type { LayoutData } from '$lib/types';

export const load = async ({ fetch }): Promise<LayoutData> => {
  let integrationStatus = null;
  let health = null;
  let apiReachable = true;

  try {
    [integrationStatus, health] = await Promise.all([getIntegrationStatus(fetch), getHealth(fetch)]);
  } catch {
    apiReachable = false;
  }

  return {
    integrationStatus,
    health,
    apiReachable
  };
};

