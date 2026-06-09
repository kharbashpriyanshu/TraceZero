"""
scanner/duplicate_scanner.py — TraceZero

Scanner module for finding duplicate files in user directories.
Uses an optimized approach:
1. Groups files by size.
2. For files with identical sizes, calculates the hash (MD5/SHA256) of the first 4KB.
3. If partial hashes match, calculates full hash to confirm duplicates.
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

from tracezero.utils.logger import app_logger

class DuplicateScanner:
    def __init__(self):
        self.chunk_size = 8192
        
    def scan(self, target_directories: List[str]) -> List[List[Dict]]:
        """
        Scans given directories and returns a list of duplicate groups.
        Each group is a list of file dictionaries with identical content.
        """
        app_logger.info(f"Starting duplicate scan on {len(target_directories)} directories...")
        
        # Step 1: Group by file size
        size_groups = defaultdict(list)
        for directory in target_directories:
            if not os.path.exists(directory):
                continue
                
            for root, dirs, files in os.walk(directory):
                # Skip common system or hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('AppData', 'Windows', 'Program Files', 'Program Files (x86)')]
                
                for f in files:
                    file_path = os.path.join(root, f)
                    try:
                        # Follow symlinks can cause issues, use lstat or just ignore them
                        if os.path.islink(file_path):
                            continue
                        size = os.path.getsize(file_path)
                        # Ignore 0-byte files or very small files (< 1KB) to speed up and reduce noise
                        if size > 1024:
                            size_groups[size].append(file_path)
                    except Exception:
                        pass
                        
        # Filter out unique sizes
        potential_duplicates = {size: paths for size, paths in size_groups.items() if len(paths) > 1}
        
        # Step 2: Group by partial hash (first 4KB)
        partial_hash_groups = defaultdict(list)
        for size, paths in potential_duplicates.items():
            for path in paths:
                partial_hash = self._get_partial_hash(path)
                if partial_hash:
                    partial_hash_groups[(size, partial_hash)].append(path)
                    
        # Filter out unique partial hashes
        suspected_duplicates = {k: paths for k, paths in partial_hash_groups.items() if len(paths) > 1}
        
        # Step 3: Group by full hash
        duplicate_results = []
        for (size, _), paths in suspected_duplicates.items():
            full_hash_groups = defaultdict(list)
            for path in paths:
                full_hash = self._get_full_hash(path)
                if full_hash:
                    full_hash_groups[full_hash].append(path)
                    
            for hash_val, dup_paths in full_hash_groups.items():
                if len(dup_paths) > 1:
                    # Construct result dict
                    group = []
                    for p in dup_paths:
                        group.append({
                            "path": p,
                            "name": os.path.basename(p),
                            "size_bytes": size,
                            "hash": hash_val
                        })
                    duplicate_results.append(group)
                    
        app_logger.info(f"Duplicate scan complete. Found {len(duplicate_results)} duplicate groups.")
        return duplicate_results
        
    def _get_partial_hash(self, file_path: str) -> str:
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(4096)
                if not chunk:
                    return None
                return hashlib.md5(chunk).hexdigest()
        except Exception:
            return None
            
    def _get_full_hash(self, file_path: str) -> str:
        try:
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(self.chunk_size), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None
