"""
utils/network_cleaner.py  — TraceZero

Handles OS-level privacy sweeping tasks such as flushing the DNS cache,
which resolves the issue of incognito mode leaking domain lookups via DNS.
"""

import subprocess
from tracezero.utils.logger import app_logger

class NetworkCleaner:
    @staticmethod
    def flush_dns() -> bool:
        """
        Flushes the Windows DNS Resolver Cache to remove traces of visited domains
        (including those visited in Incognito/Private Browsing modes).
        """
        try:
            app_logger.info("Flushing DNS cache to remove incognito traces...")
            # Using subprocess to run ipconfig /flushdns securely
            result = subprocess.run(
                ["ipconfig", "/flushdns"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                app_logger.info("Successfully flushed DNS cache.")
                return True
            else:
                app_logger.warning(f"Failed to flush DNS cache. Output: {result.stdout}")
                return False
                
        except Exception as e:
            app_logger.error(f"Error while flushing DNS cache: {e}", exc_info=True)
            return False
