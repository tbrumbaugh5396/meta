"""Atomic transaction support for vendor conversions."""

import shutil
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from meta.utils.logger import log, error, success, warning
from meta.utils.vendor_backup import create_backup, restore_backup


TRANSACTION_DIR = Path(".meta/transactions")


class ConversionTransaction:
    """Manages an atomic conversion transaction."""
    
    def __init__(self, transaction_id: str):
        self.transaction_id = transaction_id
        self.transaction_dir = TRANSACTION_DIR / transaction_id
        self.transaction_dir.mkdir(parents=True, exist_ok=True)
        self.backup_path: Optional[Path] = None
        self.rollback_actions: List[Callable] = []
        self.committed = False
        self.rolled_back = False
    
    def create_checkpoint(self, backup_name: Optional[str] = None) -> bool:
        """Create a checkpoint (backup) for this transaction.
        
        Args:
            backup_name: Optional name for backup
        
        Returns:
            True if successful
        """
        from meta.utils.vendor_backup import create_backup
        
        backup_name = backup_name or f"transaction_{self.transaction_id}"
        self.backup_path = create_backup(backup_name, include_components=True)
        
        if self.backup_path:
            # Save backup path in transaction metadata
            metadata = {
                'transaction_id': self.transaction_id,
                'backup_path': str(self.backup_path),
                'created_at': datetime.utcnow().isoformat() + "Z"
            }
            metadata_path = self.transaction_dir / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            return True
        return False
    
    def add_rollback_action(self, action: Callable):
        """Add a rollback action to be executed if transaction fails.
        
        Args:
            action: Callable to execute during rollback
        """
        self.rollback_actions.append(action)
    
    def commit(self) -> bool:
        """Commit the transaction (mark as successful).
        
        Returns:
            True if successful
        """
        if self.committed:
            warning("Transaction already committed")
            return True
        
        self.committed = True
        
        # Save commit metadata
        metadata_path = self.transaction_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        metadata['committed'] = True
        metadata['committed_at'] = datetime.utcnow().isoformat() + "Z"
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        success(f"Transaction {self.transaction_id} committed")
        return True
    
    def rollback(self) -> bool:
        """Rollback the transaction.
        
        Returns:
            True if successful
        """
        if self.rolled_back:
            warning("Transaction already rolled back")
            return True
        
        if self.committed:
            error("Cannot rollback committed transaction")
            return False
        
        log(f"Rolling back transaction {self.transaction_id}")
        
        # Execute rollback actions in reverse order
        for action in reversed(self.rollback_actions):
            try:
                action()
            except Exception as e:
                error(f"Rollback action failed: {e}")
        
        # Restore from backup if available
        if self.backup_path and self.backup_path.exists():
            from meta.utils.vendor_backup import restore_backup
            backup_name = self.backup_path.name
            if restore_backup(backup_name, restore_components=True):
                success(f"Restored from backup: {backup_name}")
            else:
                error(f"Failed to restore from backup: {backup_name}")
                return False
        
        self.rolled_back = True
        
        # Save rollback metadata
        metadata_path = self.transaction_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {}
        
        metadata['rolled_back'] = True
        metadata['rolled_back_at'] = datetime.utcnow().isoformat() + "Z"
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        success(f"Transaction {self.transaction_id} rolled back")
        return True
    
    def cleanup(self):
        """Clean up transaction directory (after successful commit)."""
        if self.transaction_dir.exists() and self.committed:
            # Keep metadata but remove temporary files
            # (backup is kept separately)
            pass


def create_transaction(transaction_id: Optional[str] = None) -> ConversionTransaction:
    """Create a new conversion transaction.
    
    Args:
        transaction_id: Optional transaction ID (defaults to UUID)
    
    Returns:
        ConversionTransaction instance
    """
    import uuid
    
    if not transaction_id:
        transaction_id = str(uuid.uuid4())[:8]
    
    return ConversionTransaction(transaction_id)


def atomic_conversion(
    conversion_func: Callable,
    *args,
    create_checkpoint: bool = True,
    **kwargs
) -> bool:
    """Execute a conversion function atomically.
    
    Args:
        conversion_func: Function to execute
        *args: Arguments to pass to conversion function
        create_checkpoint: Whether to create backup checkpoint
        **kwargs: Keyword arguments to pass to conversion function
    
    Returns:
        True if successful, False otherwise
    """
    transaction = create_transaction()
    
    try:
        # Create checkpoint
        if create_checkpoint:
            if not transaction.create_checkpoint():
                error("Failed to create checkpoint")
                return False
        
        # Execute conversion
        log(f"Executing conversion in transaction {transaction.transaction_id}")
        result = conversion_func(*args, **kwargs)
        
        if result:
            # Commit transaction
            transaction.commit()
            transaction.cleanup()
            return True
        else:
            # Rollback on failure
            error("Conversion failed, rolling back...")
            transaction.rollback()
            return False
    
    except Exception as e:
        error(f"Conversion error: {e}")
        transaction.rollback()
        return False

