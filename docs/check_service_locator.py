#!/usr/bin/env python
"""ServiceLocator validation script for DokPotok IRIS.

Checks that all documented services exist in ServiceLocator.

Usage:
    python docs/check_service_locator.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_service_locator():
    """Check that all documented services exist in ServiceLocator."""
    print("=" * 60)
    print("ServiceLocator Validation")
    print("=" * 60)
    
    # Documented services from core/README.md and services/README.md
    documented_services = {
        'auth_service': 'Authentication and token management',
        'revision_service': 'Document revision management',
        'document_service': 'Document CRUD operations',
        'document_workflow': 'Document workflow orchestration',
        'project_dashboard': 'Project metrics and portfolio overview',
        'cpm_scheduler': 'Critical Path Method scheduling',
        'time_calculation': 'Work day/hour calculations',
        'heatmap_service': 'User workload visualization',
        'storage': 'File storage abstraction',
    }
    
    missing = []
    found = []
    
    try:
        from core.service_locator import get_locator, init_locator
        from config import Config
        
        # Initialize ServiceLocator with config
        cfg = Config()
        init_locator(cfg)
        
        locator = get_locator()
        
        print("\n[CHECKING] Documented services...")
        for service, description in documented_services.items():
            if hasattr(locator, service):
                found.append(service)
                print(f"  [OK] {service}: {description}")
            else:
                missing.append(service)
                print(f"  [MISSING] {service}: {description}")
        
    except ImportError as e:
        print(f"\n[ERROR] Failed to import ServiceLocator: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Failed to check ServiceLocator: {e}")
        return 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Found: {len(found)}/{len(documented_services)} services")
    
    if missing:
        print(f"\n[WARN] Missing services: {', '.join(missing)}")
        print("\n[ACTION REQUIRED]")
        print("1. Check if services are implemented in core/service_locator.py")
        print("2. If not implemented yet, update documentation to reflect current state")
        print("3. Run: python -c \"from core.service_locator import get_locator; print(dir(get_locator()))\"")
        return 1
    else:
        print("\n[PASSED] All documented services found")
        return 0


if __name__ == "__main__":
    sys.exit(check_service_locator())
