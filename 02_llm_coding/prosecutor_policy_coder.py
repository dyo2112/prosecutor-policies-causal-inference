"""
Prosecutor Policy Document Coding Pipeline
Extracts structured policy data from DA office documents using Claude API

Author: Dvir Karp, BERQ-J
Purpose: Analyze prosecutorial ideology across time and place
"""

import os
import json
import pandas as pd
import time
from pathlib import Path
from typing import Dict, List, Optional
import anthropic
from pypdf import PdfReader
import pdfplumber
from docx import Document
import logging
from tqdm import tqdm

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('coding_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DocumentExtractor:
    """Extract text from various document formats"""
    
    @staticmethod
    def extract_pdf(filepath: str) -> str:
        """Extract text from PDF using pdfplumber for better layout preservation"""
        try:
            text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            
            # Fallback to pypdf if pdfplumber returns nothing
            if not text.strip():
                reader = PdfReader(filepath)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF {filepath}: {e}")
            return ""
    
    @staticmethod
    def extract_docx(filepath: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(filepath)
            text = "\n\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting DOCX {filepath}: {e}")
            return ""
    
    @staticmethod
    def extract_doc(filepath: str) -> str:
        """Extract text from legacy DOC file using antiword or catdoc"""
        try:
            import subprocess
            # Try antiword first
            result = subprocess.run(
                ['antiword', filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()
            
            # Fallback to catdoc
            result = subprocess.run(
                ['catdoc', filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception as e:
            logger.error(f"Error extracting DOC {filepath}: {e}")
            return ""
    
    def extract_text(self, filepath: str) -> str:
        """Extract text from file based on extension"""
        ext = Path(filepath).suffix.lower()
        
        if ext == '.pdf':
            return self.extract_pdf(filepath)
        elif ext == '.docx':
            return self.extract_docx(filepath)
        elif ext == '.doc':
            return self.extract_doc(filepath)
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return ""


class PolicyCoder:
    """Code prosecutor policy documents using Claude API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Anthropic API key"""
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        
    def create_coding_prompt(self, document_text: str, filename: str, county: str, 
                            relevant_date: str) -> str:
        """Create the structured coding prompt for Claude"""
        
        prompt = f"""You are a political science and criminal justice researcher coding prosecutor office policy documents. Your task is to extract structured information about prosecutorial ideology and policy orientation.

DOCUMENT METADATA:
- Filename: {filename}
- County: {county}
- Date: {relevant_date}

DOCUMENT TEXT:
{document_text[:50000]}  # Truncate if needed to fit in context

Please analyze this document and provide a structured coding in JSON format. Use the coding schema below:

CODING SCHEMA:

1. DOCUMENT CLASSIFICATION
   - document_type: [policy_memo, training_material, general_memo, procedure_manual, case_guidance, charging_standard, sentencing_guidance, diversion_protocol, bail_schedule, other]
   - primary_topic: [charging_decisions, sentencing, bail, diversion, enhancements, three_strikes, juvenile, death_penalty, racial_justice, discovery, victim_services, case_law_update, administrative, other]
   - secondary_topics: [list any additional topics]

2. EXTENSIVE VS INTENSIVE MARGIN
The "extensive margin" refers to decisions about WHO enters the criminal justice system (charging, declination, diversion).
The "intensive margin" refers to decisions about HOW SEVERELY people already in the system are treated (sentencing, enhancements, plea offers).

Code each as: high_impact, moderate_impact, low_impact, or not_applicable

   - extensive_margin_impact: [your assessment]
   - extensive_margin_direction: [more_lenient, more_punitive, neutral, mixed, not_applicable]
   - extensive_margin_explanation: [2-3 sentence explanation]
   
   - intensive_margin_impact: [your assessment]
   - intensive_margin_direction: [more_lenient, more_punitive, neutral, mixed, not_applicable]
   - intensive_margin_explanation: [2-3 sentence explanation]

3. PROGRESSIVE VS TRADITIONAL PROSECUTORIAL IDEOLOGY
Progressive indicators: diversion programs, declination policies, racial justice focus, reduced enhancements, bail reform, alternatives to incarceration, restorative justice, implicit bias training
Traditional indicators: strict charging, enhancement maximization, three strikes advocacy, high bail, tough-on-crime rhetoric, victim-centered only

   - ideological_orientation: [clearly_progressive, leans_progressive, neutral, leans_traditional, clearly_traditional, mixed, unclear]
   - confidence_level: [high, medium, low]
   - progressive_indicators: [list specific progressive elements]
   - traditional_indicators: [list specific traditional elements]
   - ideological_explanation: [3-5 sentence explanation of your coding]

4. SPECIFIC POLICY POSITIONS (if applicable)
   - supports_diversion: [yes, no, unclear, not_addressed]
   - supports_alternatives_to_incarceration: [yes, no, unclear, not_addressed]
   - position_on_enhancements: [maximize, selective, minimize, not_addressed]
   - position_on_three_strikes: [strict_enforcement, flexible, reform_oriented, not_addressed]
   - position_on_bail: [high_bail, moderate, reform_oriented, not_addressed]
   - position_on_juvenile_transfer: [supports_transfer, case_by_case, opposes_transfer, not_addressed]
   - racial_justice_emphasis: [high, moderate, low, not_addressed]

5. ADMINISTRATIVE CONTEXT
   - da_administration_mentioned: [name if mentioned, or "not_mentioned"]
   - reflects_office_wide_policy: [yes, no, unclear]
   - policy_change_indicator: [clearly_new_policy, modification, continuation, unclear]
   - mandates_vs_guidance: [mandatory, strong_guidance, suggestion, informational]

6. KEY QUOTES
Extract 2-3 most relevant quotes that illustrate the ideological orientation or policy position (include exact text and specify if this is extensive or intensive margin)

7. SUMMARY
Provide a 3-4 sentence summary of the document's main purpose and policy implications.

CRITICAL INSTRUCTIONS:
- Base your coding ONLY on the document text provided
- If information is unclear or not present, mark as "unclear" or "not_addressed"
- For ideological coding, look at the totality of emphasis, framing, and concrete policy choices
- Consider what the document prioritizes vs what it de-emphasizes
- Be precise in distinguishing extensive vs intensive margin impacts

Return your analysis as a valid JSON object with all fields filled in."""

        return prompt
    
    def code_document(self, document_text: str, filename: str, county: str, 
                     relevant_date: str, retry_count: int = 3) -> Optional[Dict]:
        """Send document to Claude for coding with retry logic"""
        
        if not document_text or len(document_text) < 100:
            logger.warning(f"Document too short or empty: {filename}")
            return None
        
        prompt = self.create_coding_prompt(document_text, filename, county, relevant_date)
        
        for attempt in range(retry_count):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    temperature=0.1,  # Low temperature for consistent coding
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                # Extract JSON from response
                response_text = message.content[0].text
                
                # Try to find JSON in the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    result = json.loads(json_str)
                    
                    # Add metadata
                    result['filename'] = filename
                    result['county'] = county
                    result['relevant_date'] = relevant_date
                    result['coded_at'] = pd.Timestamp.now().isoformat()
                    
                    return result
                else:
                    logger.error(f"No JSON found in response for {filename}")
                    
            except anthropic.RateLimitError:
                wait_time = (attempt + 1) * 60  # Exponential backoff
                logger.warning(f"Rate limit hit, waiting {wait_time}s...")
                time.sleep(wait_time)
                
            except Exception as e:
                logger.error(f"Error coding {filename} (attempt {attempt+1}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(5)
        
        return None


class PipelineManager:
    """Manage the full document coding pipeline"""
    
    def __init__(self, documents_dir: str, metadata_file: str, output_file: str,
                 api_key: Optional[str] = None):
        self.documents_dir = Path(documents_dir)
        self.metadata_file = metadata_file
        self.output_file = output_file
        
        self.extractor = DocumentExtractor()
        self.coder = PolicyCoder(api_key)
        
        # Load metadata
        self.metadata = pd.read_csv(metadata_file)
        logger.info(f"Loaded metadata for {len(self.metadata)} documents")
        
        # Load existing results if available
        self.results = []
        if os.path.exists(output_file):
            existing = pd.read_csv(output_file)
            self.results = existing.to_dict('records')
            logger.info(f"Loaded {len(self.results)} existing results")
    
    def get_already_coded(self) -> set:
        """Get set of filenames already coded"""
        return {r['filename'] for r in self.results}
    
    def find_document_file(self, filename: str) -> Optional[Path]:
        """Find the actual file path for a document"""
        # Try exact match first
        exact_path = self.documents_dir / filename
        if exact_path.exists():
            return exact_path
        
        # Try case-insensitive search
        for file in self.documents_dir.glob('*'):
            if file.name.lower() == filename.lower():
                return file
        
        return None
    
    def process_document(self, row: pd.Series) -> Optional[Dict]:
        """Process a single document"""
        filename = row['filename']
        
        # Find file
        filepath = self.find_document_file(filename)
        if not filepath:
            logger.warning(f"File not found: {filename}")
            return None
        
        # Extract text
        logger.info(f"Extracting text from {filename}")
        text = self.extractor.extract_text(str(filepath))
        
        if not text:
            logger.warning(f"No text extracted from {filename}")
            return None
        
        # Code document
        logger.info(f"Coding {filename} ({len(text)} chars)")
        result = self.coder.code_document(
            text, 
            filename,
            row['county'],
            str(row.get('relevant_date', ''))
        )
        
        return result
    
    def run_pipeline(self, batch_size: int = 50, start_idx: int = 0, 
                     max_docs: Optional[int] = None):
        """Run the full pipeline with batching and checkpointing"""
        
        already_coded = self.get_already_coded()
        to_process = self.metadata[~self.metadata['filename'].isin(already_coded)]
        
        if start_idx > 0:
            to_process = to_process.iloc[start_idx:]
        
        if max_docs:
            to_process = to_process.head(max_docs)
        
        logger.info(f"Processing {len(to_process)} documents")
        
        for i, (idx, row) in enumerate(tqdm(to_process.iterrows(), total=len(to_process))):
            try:
                result = self.process_document(row)
                
                if result:
                    self.results.append(result)
                    logger.info(f"Successfully coded {row['filename']}")
                
                # Checkpoint every batch_size documents
                if (i + 1) % batch_size == 0:
                    self.save_results()
                    logger.info(f"Checkpoint: Saved {len(self.results)} results")
                
                # Rate limiting - be respectful of API
                time.sleep(2)  # 2 seconds between requests
                
            except Exception as e:
                logger.error(f"Failed to process {row['filename']}: {e}")
        
        # Final save
        self.save_results()
        logger.info(f"Pipeline complete. Total coded: {len(self.results)}")
    
    def save_results(self):
        """Save results to CSV"""
        if not self.results:
            return
        
        df = pd.DataFrame(self.results)
        df.to_csv(self.output_file, index=False)
        logger.info(f"Saved {len(df)} results to {self.output_file}")


def main():
    """Main entry point"""
    from pathlib import Path

    # Configuration - use project structure
    SCRIPT_DIR = Path(__file__).parent
    PROJECT_ROOT = SCRIPT_DIR.parent

    DOCUMENTS_DIR = PROJECT_ROOT / "aclu_prosecutor_policies" / "documents"
    METADATA_FILE = PROJECT_ROOT / "01_raw_data" / "prosecutor_policies_metadata.csv"
    OUTPUT_FILE = PROJECT_ROOT / "05_data" / "intermediate" / "coded_prosecutor_policies.csv"
    
    # Initialize pipeline
    pipeline = PipelineManager(
        documents_dir=DOCUMENTS_DIR,
        metadata_file=METADATA_FILE,
        output_file=OUTPUT_FILE
    )
    
    # Run pipeline
    # Start with a small batch to test (e.g., max_docs=10)
    pipeline.run_pipeline(
        batch_size=50,
        start_idx=0,
        max_docs=None  # Test with 10 documents first
    )


if __name__ == "__main__":
    main()
