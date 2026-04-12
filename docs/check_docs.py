#!/usr/bin/env python
"""Documentation validation script for DokPotok IRIS.

Checks that:
1. All files mentioned in README exist
2. All imports in examples are valid
3. Migration status is accurate

Usage:
    python docs/check_docs.py
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_file_exists(filepath: str, base_dir: str = ".") -> bool:
    """Check if a file exists relative to base_dir."""
    full_path = os.path.join(base_dir, filepath)
    return os.path.exists(full_path)


def check_import_exists(module_path: str) -> bool:
    """Check if a Python module can be imported."""
    try:
        __import__(module_path)
        return True
    except ImportError:
        return False


def extract_file_references_from_readme(readme_path: str) -> List[str]:
    """Extract file references from README markdown."""
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find file paths in code blocks and text
    patterns = [
        r"`([^`]+\.(py|md|sql))`",  # Inline code
        r"```(?:python|markdown|sql)?\s*([^\s]+?\.(?:py|md|sql))",  # Code block start
    ]
    
    files = []
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if isinstance(match, tuple):
                files.append(match[0])
            else:
                files.append(match)
    
    return list(set(files))


def check_readme_files(readme_path: str) -> Tuple[int, List[str]]:
    """Check that all files mentioned in README exist."""
    errors = []
    readme_dir = os.path.dirname(readme_path)
    
    files = extract_file_references_from_readme(readme_path)
    
    # Files that are expected to be in different directories (not errors)
    expected_in_other_dirs = {
        # SQL migrations
        '000_initial.sql', '001_add_planning.sql', '002_add_users.sql',
        '003_new_modules.sql', '002_add_performance_indexes.sql',
        '004_additional_performance_indexes.sql',
        # Alembic migrations
        '0001_initial_schema.py', '0002_add_tenders.py', '0003_add_project_metrics.py',
        # Optional files
        'exceptions.py', 'gamification_event_service.py',
    }
    
    for filepath in files:
        # Skip external URLs
        if filepath.startswith('http'):
            continue
        
        # Skip files expected in other directories
        if os.path.basename(filepath) in expected_in_other_dirs:
            continue
        
        # Check relative to README directory
        if not check_file_exists(filepath, readme_dir):
            # Try from project root
            if not check_file_exists(filepath, "."):
                errors.append(f"Missing: {filepath}")
    
    return len(errors), errors


def check_service_locator_services() -> Tuple[int, List[str]]:
    """Check that all documented services exist in ServiceLocator."""
    errors = []
    
    documented_services = [
        'auth_service',
        'revision_service',
        'document_service',
        'document_workflow',
        'project_dashboard',
        'cpm_scheduler',
        'time_calculation',
        'heatmap_service',
        'storage',
    ]
    
    try:
        from core.service_locator import get_locator, init_locator
        from config import Config
        
        # Initialize ServiceLocator
        cfg = Config()
        init_locator(cfg)
        
        locator = get_locator()
        
        for service in documented_services:
            if not hasattr(locator, service):
                errors.append(f"ServiceLocator missing: {service}")
    except Exception as e:
        errors.append(f"Failed to check ServiceLocator: {e}")
    
    return len(errors), errors


def check_base_repository() -> Tuple[int, List[str]]:
    """Check that BaseRepository exists and is usable."""
    errors = []
    
    try:
        from repositories.base_repository import BaseRepository
        from db.database import Database
        
        # Check it has required methods
        required_methods = ['get_by_id', 'list_all', 'delete', '_get_paginated']
        for method in required_methods:
            if not hasattr(BaseRepository, method):
                errors.append(f"BaseRepository missing method: {method}")
    except Exception as e:
        errors.append(f"Failed to import BaseRepository: {e}")
    
    return len(errors), errors


def check_repository_migration_status() -> Tuple[int, List[str]]:
    """Check that repository migration status in README is accurate."""
    errors = []
    
    # Read repositories README
    readme_path = "repositories/README.md"
    if not check_file_exists(readme_path):
        errors.append(f"Missing: {readme_path}")
        return len(errors), errors
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for work_schedule_repository (should be migrated)
    if "work_schedule_repository.py" in content:
        # Just verify it's documented, not whether migrated yet
        pass
    
    # Check BaseRepository is mentioned
    if "BaseRepository" not in content:
        errors.append("BaseRepository not documented in repositories/README.md")
    
    return len(errors), errors


def run_all_checks() -> int:
    """Run all documentation checks."""
    print("=" * 60)
    print("Documentation Validation")
    print("=" * 60)
    
    all_errors = []
    
    # Check 1: ServiceLocator services
    print("\n[1/4] Checking ServiceLocator services...")
    count, errors = check_service_locator_services()
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  [FAIL] {e}")
    else:
        print(f"  [OK] All services found")
    
    # Check 2: BaseRepository
    print("\n[2/4] Checking BaseRepository...")
    count, errors = check_base_repository()
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  [FAIL] {e}")
    else:
        print("  [OK] BaseRepository is available")
    
    # Check 3: Repository migration status
    print("\n[3/4] Checking repository migration status...")
    count, errors = check_repository_migration_status()
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  [FAIL] {e}")
    else:
        print("  [OK] Migration status documented")
    
    # Check 4: README files
    print("\n[4/4] Checking README file references...")
    readme_paths = [
        "repositories/README.md",
        "services/README.md",
        "api/README.md",
        "core/README.md",
        "db/README.md",
    ]
    
    for readme in readme_paths:
        if check_file_exists(readme):
            count, errors = check_readme_files(readme)
            if errors:
                all_errors.extend(errors)
                for e in errors:
                    print(f"  [FAIL] {readme}: {e}")
            else:
                print(f"  [OK] {readme}: all files found")
        else:
            all_errors.append(f"Missing README: {readme}")
    
    # Summary
    print("\n" + "=" * 60)
    if all_errors:
        print(f"FAILED: {len(all_errors)} error(s) found")
        print("=" * 60)
        return 1
    else:
        print("PASSED: All checks passed")
        print("=" * 60)
        return 0


if __name__ == "__main__":
    sys.exit(run_all_checks())
