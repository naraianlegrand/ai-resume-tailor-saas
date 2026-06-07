"""Service module for parsing uploaded files."""

import io
import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class ParserService:
    """Service to extract text contents from various file formats."""

    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        """Extracts text from PDF file bytes.

        Args:
            file_bytes: Raw bytes of the uploaded PDF file.

        Returns:
            Extracted text content from the PDF.

        Raises:
            ValueError: If the PDF is empty or invalid.
            Exception: For general parsing errors.
        """
        try:
            if not file_bytes:
                raise ValueError("Empty file bytes provided")

            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)

            text_parts = []
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                else:
                    logger.debug("No extractable text on page %d", i + 1)

            full_text = "\n".join(text_parts).strip()
            if not full_text:
                raise ValueError("Could not extract any text content from the PDF file")

            logger.info("Successfully extracted %d characters from PDF", len(full_text))
            return full_text

        except ValueError as val_err:
            logger.warning("Validation error in PDF parsing: %s", str(val_err))
            raise val_err
        except Exception as exc:
            logger.error("Failed to parse PDF file: %s", str(exc), exc_info=True)
            raise exc
