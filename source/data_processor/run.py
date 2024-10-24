import os
import logging
from typing import List, Optional
import pandas as pd
from pathlib import Path
from .clean_data import DataProcessor
from .merge_data import DataMerger
from .clone_data import download_superapp_data
from .convert_data import DataConverter
from .indexing_data import DataIndexer
from configs.config_system import LoadConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataProcessingPipeline:
    def __init__(self, config: LoadConfig = LoadConfig()):
        self.config = config
        
    def create_directory_structure(self, member_code: str) -> None:
        """Create necessary directory structure for data processing."""
        try:
            Path(self.config.SPECIFIC_PRODUCT_FOLDER_CSV_STORAGE.format(
                member_code=member_code)).mkdir(parents=True, exist_ok=True)
            Path(self.config.SPECIFIC_PRODUCT_FOLDER_TXT_STORAGE.format(
                member_code=member_code)).mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory structure for member {member_code}")
        except Exception as e:
            logger.error(f"Failed to create directories for {member_code}: {str(e)}")
            raise

    def process_single_member(
        self,
        member_code: str,
        all_data_path: str,
        data_available_path: str
    ) -> None:
        """Process data for a single member."""
        try:
            self.create_directory_structure(member_code)
            
            # Download data
            # data = download_superapp_data(member_code)
            data = pd.read_excel("data/data_private/data_member/data_final_G-JLVIYR.xlsx")
            if data is None or data.empty:
                logger.warning(f"No data available for member {member_code}")
                return

            # Process raw data
            processed_df = self._process_raw_data(data, member_code, all_data_path)
            
            # Merge data
            merged_df = self._merge_data(
                member_code, 
                all_data_path, 
                data_available_path
            )
            
            # Convert and index data
            self._convert_and_index_data(member_code)
            
            logger.info(f"Successfully processed all data for member {member_code}")
            
        except Exception as e:
            logger.error(f"Error processing member {member_code}: {str(e)}")
            raise

    @staticmethod
    def _process_raw_data(
        data: pd.DataFrame, 
        member_code: str,
        all_data_path: str
    ) -> pd.DataFrame:
        """Process raw data using DataProcessor."""
        processor = DataProcessor(data)
        processed_df = processor.process().sort_values(by='productGroupId')
        output_path = all_data_path.format(member_code=member_code)
        processed_df.to_excel(output_path, index=False)
        logger.info(f"Processed raw data for member {member_code}")
        return processed_df

    @staticmethod
    def _merge_data(
        member_code: str,
        all_data_path: str,
        data_available_path: str
    ) -> pd.DataFrame:
        """Merge and group data."""
        new_data_path = all_data_path.format(member_code=member_code)
        output_path = all_data_path.format(member_code=f"{member_code}_merged")
        
        merger = DataMerger(
            origin_data_path=data_available_path,
            new_data_path=new_data_path,
            merged_file_path=output_path
        )
        
        merged_df = merger.mergering()
        merger.group_data(member_code, merged_df)
        logger.info(f"Merged and grouped data for member {member_code}")
        return merged_df

    @staticmethod
    def _convert_and_index_data(member_code: str) -> None:
        """Convert data to text and create indices."""
        # Convert to text
        converter = DataConverter(member_code=member_code)
        converter.process_data()
        
        # Create indices
        indexer = DataIndexer()
        indexer.restart_index_name()
        indexer.embedding_all_product()
        logger.info(f"Converted and indexed data for member {member_code}")

    def processing(
        self,
        all_data_path: str,
        data_available_path: str = "data/data_private/product_final_300_extract.xlsx",
        member_codes: Optional[List[str]] = None
    ) -> None:
        
        """Process data for all specified members."""
        if all_data_path is None:
            all_data_path = self.config.ALL_PRODUCT_FILE_CSV_STORAGE
        if member_codes is None:
            member_codes = self.config.MEMBER_CODE

        for member_code in member_codes:
            if member_code != "G-JLVIYR":  # TODO: Remove this condition if not needed
                continue
            logger.info(f"Starting processing for member {member_code}")
            try:
                self.process_single_member(
                    member_code,
                    all_data_path,
                    data_available_path
                )
            except Exception as e:
                logger.error(f"Failed to process member {member_code}: {str(e)}")
                continue

def main():
    """Main entry point for the data processing pipeline."""
    try:
        pipeline = DataProcessingPipeline()
        pipeline.process_all_members()
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")

if __name__ == "__main__":
    main()