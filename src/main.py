"""
Main entry point for vision-based nutrition label parser.

Simple architecture:
1. Detect valid nutrition images (filter invalid)
2. Extract nutrients using vision model
3. Validate amounts (anti-hallucination)
4. Export to CSV
"""
import argparse
import logging
import os
from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

from src.utils.logger import setup_logger
from src.utils.file_utils import find_image_files, ensure_directory
from src.vision.model_interface import VisionModelFactory
from src.vision.detector import NutritionDataDetector
from src.vision.extractor import NutritionExtractor
from src.models.entities import NutrientRecord

logger = logging.getLogger(__name__)


class VisionNutritionPipeline:
    """Simplified vision-based nutrition extraction pipeline."""
    
    def __init__(
        self,
        provider: str = "auto",
        model: str = None,
        skip_detection: bool = False
    ):
        """
        Initialize pipeline.
        
        Args:
            provider: Vision model provider (openai/claude/gemini/auto)
            model: Specific model name (optional)
            skip_detection: Skip nutrition data detection step
        """
        logger.info(f"Initializing vision pipeline with provider: {provider}")
        
        # Create vision model
        model_kwargs = {"model": model} if model else {}
        self.vision_model = VisionModelFactory.create(provider, **model_kwargs)
        
        # Initialize components
        self.detector = NutritionDataDetector(self.vision_model)
        self.extractor = NutritionExtractor(self.vision_model)
        self.skip_detection = skip_detection
    
    def process_single_image(self, image_path: Path) -> dict:
        """
        Process a single image.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dict with records and metadata
        """
        try:
            # Step 1: Detect if image has nutrition data
            if not self.skip_detection:
                detection = self.detector.has_nutrition_data(image_path)
                
                if not detection["has_data"]:
                    logger.info(f"Skipping {image_path.name}: {detection['reason']}")
                    return {
                        "records": [],
                        "skipped": True,
                        "reason": detection["reason"]
                    }
            
            # Step 2: Extract nutrients
            extraction = self.extractor.extract(image_path)
            
            return {
                "records": extraction["nutrients"],
                "skipped": False,
                "confidence": extraction["confidence"],
                "ambiguities": extraction.get("ambiguities", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to process {image_path.name}: {e}")
            return {
                "records": [],
                "skipped": True,
                "reason": f"Processing error: {str(e)}"
            }
    
    def process_images(self, input_dir: Path, max_workers: int = 5) -> List[NutrientRecord]:
        """
        Process all images in directory using parallel batch processing.
        
        Args:
            input_dir: Directory containing product images
            max_workers: Maximum number of parallel workers (default: 5)
        
        Returns:
            List of nutrient records
        """
        # Find images
        image_files = find_image_files(input_dir)
        logger.info(f"Found {len(image_files)} images in {input_dir}")
        logger.info(f"Using {max_workers} parallel workers for batch processing")
        
        all_records = []
        skipped_images = []
        
        # Process images in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_image = {
                executor.submit(self.process_single_image, img): img 
                for img in image_files
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_image):
                image_path = future_to_image[future]
                try:
                    result = future.result()
                    
                    if result["skipped"]:
                        skipped_images.append({
                            "image": image_path.name,
                            "reason": result["reason"]
                        })
                        continue
                    
                    # Add records
                    if result["records"]:
                        all_records.extend(result["records"])
                        logger.info(f"✓ {image_path.name}: extracted {len(result['records'])} nutrients (confidence: {result['confidence']})")
                    else:
                        logger.warning(f"No nutrients extracted from {image_path.name}")
                        skipped_images.append({
                            "image": image_path.name,
                            "reason": "Extraction returned no nutrients"
                        })
                
                except Exception as e:
                    logger.error(f"Error processing {image_path.name}: {e}")
                    skipped_images.append({
                        "image": image_path.name,
                        "reason": f"Error: {str(e)}"
                    })
        
        # Log summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing complete:")
        logger.info(f"  Total images: {len(image_files)}")
        logger.info(f"  Successfully processed: {len(image_files) - len(skipped_images)}")
        logger.info(f"  Skipped: {len(skipped_images)}")
        logger.info(f"  Total nutrients extracted: {len(all_records)}")
        logger.info(f"{'='*60}\n")
        
        if skipped_images:
            logger.info("Skipped images:")
            for skip in skipped_images:
                logger.info(f"  - {skip['image']}: {skip['reason']}")
        
        return all_records
    
    def export_to_csv(self, records: List[NutrientRecord], output_path: Path):
        """
        Export records to CSV.
        
        Args:
            records: List of nutrient records
            output_path: Output CSV file path
        """
        if not records:
            logger.warning("No records to export")
            return
        
        # Convert to DataFrame
        data = []
        for record in records:
            data.append({
                "product_image": record.product_image,
                "source_section": record.source_section,
                "nutrient_name_raw": record.nutrient_name_raw,
                "nutrient_name_standard": record.nutrient_name_standard,
                "amount_raw": record.amount_raw,
                "amount": record.amount,
                "unit_raw": record.unit_raw,
                "unit": record.unit,
                "serving_context": record.serving_context,
                "parsing_method": record.parsing_method,
                "confidence": record.confidence,
                "notes": record.notes
            })
        
        df = pd.DataFrame(data)
        
        # Ensure output directory exists
        ensure_directory(output_path.parent)
        
        # Export
        df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(records)} records to {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Vision-based nutrition label parser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect model (tries OpenAI, Gemini, Claude in order)
  python source_code/main_vision.py --input sample_images --output output/nutrition_data.csv
  
  # Use specific provider
  python source_code/main_vision.py --input sample_images --output output/nutrition_data.csv --provider gemini
  
  # Use specific model
  python source_code/main_vision.py --input sample_images --output output/nutrition_data.csv --provider openai --model gpt-4o
  
Environment variables:
  OPENAI_API_KEY     - For OpenAI GPT-4V/4o
  GOOGLE_API_KEY     - For Google Gemini
  ANTHROPIC_API_KEY  - For Anthropic Claude
"""
    )
    
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("sample_images"),
        help="Input directory containing product images"
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/nutrition_data.csv"),
        help="Output CSV file path"
    )
    
    parser.add_argument(
        "--provider",
        choices=["auto", "openai", "claude", "gemini"],
        default=os.getenv("DEFAULT_PROVIDER", "auto"),
        help="Vision model provider (default: from .env or auto)"
    )
    
    parser.add_argument(
        "--model",
        default=os.getenv("DEFAULT_MODEL"),
        help="Specific model name (default: from .env or provider default)"
    )
    
    parser.add_argument(
        "--skip-detection",
        action="store_true",
        default=os.getenv("SKIP_DETECTION", "false").lower() == "true",
        help="Skip nutrition data detection (default: from .env or false)"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=int(os.getenv("MAX_WORKERS", "5")),
        help="Number of parallel workers (default: from .env or 5)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        default=os.getenv("DEBUG", "false").lower() == "true",
        help="Enable debug logging (default: from .env or false)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logger(name="nutri-label-parser",debug=args.debug)
    
    logger.info("Starting Vision-based Nutrition Label Parser")
    logger.info(f"Input: {args.input}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Provider: {args.provider}")
    
    try:
        # Initialize pipeline
        pipeline = VisionNutritionPipeline(
            provider=args.provider,
            model=args.model,
            skip_detection=args.skip_detection
        )
        
        # Process images with batch processing
        records = pipeline.process_images(args.input, max_workers=args.workers)
        
        # Export results
        pipeline.export_to_csv(records, args.output)
        
        logger.info("✓ Processing complete!")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
