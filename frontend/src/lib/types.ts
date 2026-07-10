export type IntegrationStatus = {
  gemini_configured: boolean;
  groq_configured: boolean;
  alpha_vantage_configured: boolean;
  fmp_configured: boolean;
  database_configured: boolean;
  r2_configured: boolean;
  sec_user_agent_configured: boolean;
  unavailable_features: string[];
};

export type HealthResponse = {
  status: string;
  timestamp: string;
  database_configured: boolean;
  environment: string;
};

export type UploadBatchResponse = {
  upload_id: string;
  upload_type: string;
  status: string;
  file_count: number;
  parsed_rows: number;
  warning_count: number;
  error_count: number;
};

export type ParsePreviewWarning = {
  source_file: string;
  row_number: number | null;
  warning_type: string;
  warning_message: string;
};

export type ParsePreviewResponse = {
  upload_id: string;
  detected_file_types: string[];
  parsed_transaction_count: number;
  detected_date_range: [string | null, string | null];
  detected_tickers: string[];
  detected_currencies: string[];
  detected_transaction_types: string[];
  warning_rows: ParsePreviewWarning[];
  unparsed_rows: Record<string, unknown>[];
  missing_keys: string[];
  disabled_features: string[];
};

export type MetricCard = {
  name: string;
  score: number;
  explanation: string;
  payload: Record<string, unknown>;
};

export type CapitalFlowItem = {
  label: string;
  value: number;
  detail: string;
};

export type TradeReviewItem = {
  ticker: string;
  trade_date: string | null;
  review_priority: string;
  behavioral_signal: string;
  notes: string;
};

export type DataQualitySection = {
  parsed_rows: number;
  warning_rows: number;
  unknown_rows: number;
  unsupported_files: string[];
  missing_keys: string[];
  disabled_features: string[];
};

export type ReportSummary = {
  trading_personality: string;
  overall_behavior_score: number;
  main_strength: string;
  main_weakness: string;
  summary: string;
};

export type ReportDetailResponse = {
  report_id: string;
  upload_id: string;
  portfolio_upload_id?: string | null;
  generated_at: string;
  title: string;
  summary: ReportSummary;
  metric_cards: MetricCard[];
  capital_flow: CapitalFlowItem[];
  theme_drift: Record<string, unknown>;
  trade_review_list: TradeReviewItem[];
  data_quality: DataQualitySection;
  report_markdown: string;
  ai_available: boolean;
};

export type ReportGenerateResponse = {
  report_id: string;
  status: string;
  ai_available: boolean;
  message: string;
};

export type TickerTimelineEntry = {
  date: string | null;
  action_normalized: string;
  quantity: number | null;
  price: number | null;
  net_amount: number | null;
  description: string | null;
};

export type TickerReportResponse = {
  report_id: string;
  ticker: string;
  first_buy_date: string | null;
  latest_buy_date: string | null;
  latest_sell_date: string | null;
  total_bought: number | null;
  total_sold: number | null;
  net_invested: number | null;
  current_shares: number | null;
  average_buy_price: number | null;
  realized_events: Record<string, unknown>[];
  behavioral_note: string;
  timeline: TickerTimelineEntry[];
};

export type WarningListResponse = {
  report_id: string;
  warnings: {
    row_number: number | null;
    warning_type: string;
    warning_message: string;
    raw_payload: Record<string, unknown>;
  }[];
};

export type LayoutData = {
  integrationStatus: IntegrationStatus | null;
  health: HealthResponse | null;
  apiReachable: boolean;
};

