from io import BytesIO

import pandas as pd
import pdfplumber

from app.ai.router import AIRouter
from app.parsers.transactions import parse_transaction_dataframe
from app.schemas.domain import ParseIssue, ParsedTransactionFile


def parse_transaction_pdf_bytes(filename: str, file_bytes: bytes, ai_router: AIRouter | None = None) -> ParsedTransactionFile:
    tables_found = 0
    all_transactions = []
    warnings: list[ParseIssue] = []
    unparsed_rows: list[dict] = []
    detected_columns: dict[str, str | None] = {}

    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                header, *rows = table
                if not header:
                    continue
                tables_found += 1
                dataframe = pd.DataFrame(rows, columns=header)
                parsed = parse_transaction_dataframe(dataframe, f"{filename}#page-{page_number}", "pdf", ai_router)
                if not detected_columns:
                    detected_columns = parsed.detected_columns
                all_transactions.extend(parsed.transactions)
                warnings.extend(parsed.warnings)
                unparsed_rows.extend(parsed.unparsed_rows)

    if tables_found == 0:
        warnings.append(
            ParseIssue(
                source_file=filename,
                warning_type="unsupported_pdf",
                warning_message="The PDF did not contain any extractable tables, so it could not be parsed.",
                raw_payload={},
            )
        )

    return ParsedTransactionFile(
        source_file=filename,
        file_type="pdf",
        detected_columns=detected_columns,
        transactions=all_transactions,
        warnings=warnings,
        unparsed_rows=unparsed_rows,
    )

