"""Export service for serializing DataFrames to various formats."""
from io import BytesIO
from typing import Optional
import pandas as pd

from src.errors.app_error import AppError, ValidationError


class ExportService:
    """Service for exporting DataFrames to various formats."""

    def __init__(self):
        """Initialize export service."""
        pass

    def export_to_csv(self, df: pd.DataFrame) -> tuple[bytes, str]:
        """
        Export DataFrame to CSV format.

        Args:
            df: DataFrame to export

        Returns:
            Tuple of (csv_bytes, mime_type)
        """
        buffer = BytesIO()
        df.to_csv(buffer, index=False)
        return buffer.getvalue(), "text/csv"

    def export_to_xlsx(self, df: pd.DataFrame) -> tuple[bytes, str]:
        """
        Export DataFrame to Excel format.

        Args:
            df: DataFrame to export

        Returns:
            Tuple of (xlsx_bytes, mime_type)
        """
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Extraction")
        return buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    def export(self, df: pd.DataFrame, format: str) -> tuple[bytes, str]:
        """
        Export DataFrame to specified format.

        Args:
            df: DataFrame to export
            format: Export format (csv or xlsx)

        Returns:
            Tuple of (file_bytes, mime_type)

        Raises:
            ValidationError: If format is not supported
        """
        format_lower = format.lower()

        if format_lower == "csv":
            return self.export_to_csv(df)
        elif format_lower == "xlsx":
            return self.export_to_xlsx(df)
        else:
            raise ValidationError("Unsupported export format")


# Singleton instance
export_service = ExportService()
