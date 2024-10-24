import pandas as pd
import re
from typing import Dict, Any, List

class DataProcessor:
    """Class for processing and cleaning product data"""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.df = pd.DataFrame(data)
        self.measurement_columns = ['weight', 'volume', 'power']
    
    def process(self) -> pd.DataFrame:
        """
        Process and clean the data
        
        Returns:
            pd.DataFrame: Processed and cleaned data
        """
        # Extract measurements
        self.df['power'] = self.df['specifications'].apply(self._extract_power)
        self.df['weight'] = self.df['specifications'].apply(self._extract_weight)
        self.df['volume'] = self.df['specifications'].apply(self._extract_volume)
        
        # Clean text columns
        text_columns = ['specifications', 'shortDescription', 'productDescription']
        for column in text_columns:
            if column in self.df.columns:
                self.df[column] = self.df[column].apply(self._clean_html)
        
        # Convert data types
        self.df[self.measurement_columns] = self.df[self.measurement_columns].astype(float)
        if 'productCode' in self.df.columns:
            self.df['productCode'] = self.df['productCode'].astype(str)
            
        return self.df
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags and clean up whitespace"""
        if not text:
            return ""
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = re.sub(r'\n+', '\n', clean_text)
        return clean_text.strip()
    
    def _standardize_decimal(self, text: str) -> str:
        """Convert decimal comma to decimal point"""
        return text.replace(',', '.')
    
    def _extract_volume(self, text: str) -> float:
        """Extract volume measurements from text"""
        text = self._standardize_decimal(text)
        
        volume_liters = re.findall(r'(\d+(\.\d+)?)\s*l(?:ít)?\b', text, re.IGNORECASE)
        volume_ml = re.findall(r'(\d+(\.\d+)?)\s*ml\b', text, re.IGNORECASE)
        
        volume = 0.0
        if volume_liters:
            volume = float(volume_liters[0][0])
        if volume_ml:
            volume += float(volume_ml[0][0]) / 1000
            
        return volume
    
    def _extract_power(self, text: str) -> float:
        """Extract power measurements from text"""
        text = self._standardize_decimal(text)
        
        # Define power patterns and their multipliers
        patterns = {
            'btu': (r'(\d+(?:[.,]\d+)?)\s*btu\b', 1),
            'w': (r'(\d+(?:[.,]\d+)?)\s*w\b', 1),
            'kw': (r'(\d+(?:[.,]\d+)?)\s*kw\b', 1000),
            'vw': (r'(\d+(?:[.,]\d+)?)\s*v(?:/|\\| )?w\b', 1)
        }
        
        for pattern, multiplier in patterns.values():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                value = matches[0]
                if isinstance(value, tuple):
                    value = value[0]
                return float(value) * multiplier
                
        return 0.0
    
    def _extract_weight(self, text: str) -> float:
        """Extract weight measurements from text"""
        text = self._standardize_decimal(text)
        
        weight_kg = re.findall(r'(\d+(?:[.,]\d+)?)\s*kg\b', text, re.IGNORECASE)
        weight_g = re.findall(r'(\d+(?:[.,]\d+)?)\s*g\b', text, re.IGNORECASE)
        
        if weight_kg:
            return float(weight_kg[0])
        elif weight_g:
            return float(weight_g[0]) / 1000
            
        return 0.0