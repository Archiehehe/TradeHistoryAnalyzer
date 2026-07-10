import { getParsePreview } from '$lib/api';

export const load = async ({ fetch, params, url }) => {
  const preview = await getParsePreview(fetch, params.uploadId);

  return {
    preview,
    uploadId: params.uploadId,
    portfolioUploadId: url.searchParams.get('portfolio')
  };
};

