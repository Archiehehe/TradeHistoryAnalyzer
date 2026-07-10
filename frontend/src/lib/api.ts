import { env } from '$env/dynamic/public';
import type {
  HealthResponse,
  IntegrationStatus,
  ParsePreviewResponse,
  ReportDetailResponse,
  ReportGenerateResponse,
  TickerReportResponse,
  UploadBatchResponse,
  WarningListResponse
} from '$lib/types';

const API_BASE = (env.PUBLIC_API_BASE_URL || '/api').replace(/\/$/, '');

type FetchLike = typeof fetch;

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed with status ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function apiGet<T>(fetcher: FetchLike, path: string): Promise<T> {
  return parseResponse<T>(await fetcher(`${API_BASE}${path}`));
}

export async function getHealth(fetcher: FetchLike): Promise<HealthResponse> {
  return apiGet<HealthResponse>(fetcher, '/health');
}

export async function getIntegrationStatus(fetcher: FetchLike): Promise<IntegrationStatus> {
  return apiGet<IntegrationStatus>(fetcher, '/integrations/status');
}

export async function getParsePreview(fetcher: FetchLike, uploadId: string): Promise<ParsePreviewResponse> {
  return apiGet<ParsePreviewResponse>(fetcher, `/uploads/${uploadId}/parse-preview`);
}

export async function getReport(fetcher: FetchLike, reportId: string): Promise<ReportDetailResponse> {
  return apiGet<ReportDetailResponse>(fetcher, `/reports/${reportId}`);
}

export async function getTickerReport(fetcher: FetchLike, reportId: string, ticker: string): Promise<TickerReportResponse> {
  return apiGet<TickerReportResponse>(fetcher, `/reports/${reportId}/tickers/${ticker}`);
}

export async function getReportWarnings(fetcher: FetchLike, reportId: string): Promise<WarningListResponse> {
  return apiGet<WarningListResponse>(fetcher, `/reports/${reportId}/warnings`);
}

async function uploadFiles(path: string, files: File[], notes?: string): Promise<UploadBatchResponse> {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  if (notes) {
    formData.append('notes', notes);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    body: formData
  });
  return parseResponse<UploadBatchResponse>(response);
}

export async function uploadTransactionFiles(files: File[], notes?: string): Promise<UploadBatchResponse> {
  return uploadFiles('/uploads/transactions', files, notes);
}

export async function uploadPortfolioFiles(files: File[], notes?: string): Promise<UploadBatchResponse> {
  return uploadFiles('/uploads/portfolio', files, notes);
}

export async function generateReport(payload: {
  upload_id: string;
  portfolio_upload_id?: string;
}): Promise<ReportGenerateResponse> {
  const response = await fetch(`${API_BASE}/reports/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });
  return parseResponse<ReportGenerateResponse>(response);
}
