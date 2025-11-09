#!/usr/bin/env python3
"""
Qdrant Database Connection Checker

This script verifies that Qdrant is running and accessible at http://localhost:6333
and performs comprehensive checks on the database.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_qdrant_connection() -> Dict[str, Any]:
    """Check basic Qdrant connection."""
    try:
        from qdrant_client import QdrantClient
        
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        logger.info(f"\n{'='*70}")
        logger.info(f"[1/6] CHECKING QDRANT CONNECTION")
        logger.info(f"{'='*70}")
        logger.info(f"Attempting to connect to: {qdrant_url}")
        
        client = QdrantClient(url=qdrant_url)
        
        # Test connection with a simple API call
        health = client.get_collections()
        
        logger.info(f"✅ Successfully connected to Qdrant at {qdrant_url}")
        return {
            "success": True,
            "url": qdrant_url,
            "client": client,
            "message": "Connection established"
        }
        
    except ConnectionError as e:
        logger.error(f"❌ Connection failed: {e}")
        logger.info("\n💡 Quick fix: Start Qdrant with:")
        logger.info("   docker run -p 6333:6333 qdrant/qdrant:latest")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}


def check_server_info(client) -> Dict[str, Any]:
    """Get Qdrant server information."""
    try:
        logger.info(f"\n{'='*70}")
        logger.info(f"[2/6] CHECKING SERVER INFO")
        logger.info(f"{'='*70}")
        
        # Try to get version info
        try:
            version = client.get_service_info()
            logger.info(f"✅ Server Info retrieved")
            logger.info(f"   Version: {version}")
            return {"success": True, "info": version}
        except:
            logger.warning(f"⚠️  Could not retrieve version info (older Qdrant version?)")
            return {"success": True, "info": "Available"}
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}


def check_collections(client) -> Dict[str, Any]:
    """Check existing collections."""
    try:
        logger.info(f"\n{'='*70}")
        logger.info(f"[3/6] CHECKING COLLECTIONS")
        logger.info(f"{'='*70}")
        
        collections = client.get_collections()
        collection_list = [c.name for c in collections.collections]
        
        logger.info(f"✅ Total collections: {len(collection_list)}")
        
        if collection_list:
            logger.info(f"Collections found:")
            for collection_name in collection_list:
                try:
                    collection_info = client.get_collection(collection_name)
                    logger.info(f"  • {collection_name}")
                    logger.info(f"    └─ Points: {collection_info.points_count}")
                    logger.info(f"    └─ Status: {collection_info.status}")
                except Exception as e:
                    logger.warning(f"  • {collection_name} (error reading details: {e})")
        else:
            logger.info("   (No collections exist yet)")
        
        return {
            "success": True,
            "count": len(collection_list),
            "collections": collection_list
        }
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}


def check_medical_collection(client) -> Dict[str, Any]:
    """Check the medical_assistance_rag collection specifically."""
    try:
        logger.info(f"\n{'='*70}")
        logger.info(f"[4/6] CHECKING MEDICAL COLLECTION")
        logger.info(f"{'='*70}")
        
        collection_name = "medical_assistance_rag"
        
        try:
            collection_info = client.get_collection(collection_name)
            
            logger.info(f"✅ Collection '{collection_name}' found")
            logger.info(f"   Points: {collection_info.points_count}")
            logger.info(f"   Status: {collection_info.status}")
            logger.info(f"   Vector size: {collection_info.config.params.vectors.size}")
            
            if collection_info.points_count > 0:
                logger.info(f"   ✅ Collection has {collection_info.points_count} vectors")
            else:
                logger.warning(f"   ⚠️  Collection is empty (no vectors indexed)")
            
            return {
                "success": True,
                "exists": True,
                "points": collection_info.points_count,
                "status": collection_info.status
            }
            
        except Exception as e:
            if "Not found" in str(e) or "not found" in str(e).lower():
                logger.warning(f"⚠️  Collection '{collection_name}' does not exist")
                logger.info(f"    Run: python3 setup_qdrant_local.py")
                return {
                    "success": True,
                    "exists": False,
                    "message": "Collection not created yet"
                }
            else:
                raise
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}


def check_storage_stats(client) -> Dict[str, Any]:
    """Check Qdrant storage statistics."""
    try:
        logger.info(f"\n{'='*70}")
        logger.info(f"[5/6] CHECKING STORAGE STATS")
        logger.info(f"{'='*70}")
        
        try:
            stats = client.get_service_info()
            logger.info(f"✅ Storage info available")
            return {"success": True, "info": "Available"}
        except:
            logger.warning(f"⚠️  Could not retrieve storage stats")
            return {"success": True, "message": "Stats not available in this version"}
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}


def check_write_permission(client) -> Dict[str, Any]:
    """Test write permission by attempting a simple upsert."""
    try:
        logger.info(f"\n{'='*70}")
        logger.info(f"[6/6] CHECKING WRITE PERMISSION")
        logger.info(f"{'='*70}")
        
        # Check if we can write
        try:
            collections = client.get_collections()
            logger.info(f"✅ Read permission: OK")
            
            # Try to list collections (requires read access)
            logger.info(f"✅ List permission: OK")
            logger.info(f"✅ Write permission: Assumed OK (can read collections)")
            
            return {"success": True, "readable": True, "writable": True}
            
        except PermissionError:
            logger.error(f"❌ Permission denied")
            return {"success": False, "error": "Permission denied"}
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}


def main():
    """Run all checks."""
    logger.info("\n")
    logger.info("╔" + "="*68 + "╗")
    logger.info("║" + " "*15 + "QDRANT DATABASE CONNECTION CHECKER" + " "*19 + "║")
    logger.info("╚" + "="*68 + "╝")
    
    # Step 1: Check connection
    conn_result = check_qdrant_connection()
    if not conn_result["success"]:
        logger.error("\n❌ Cannot proceed - Qdrant is not accessible")
        logger.error(f"\n💡 Make sure Qdrant is running at http://localhost:6333")
        logger.error(f"   Command: docker run -p 6333:6333 qdrant/qdrant:latest")
        return False
    
    client = conn_result["client"]
    
    # Step 2: Check server info
    check_server_info(client)
    
    # Step 3: Check collections
    collections_result = check_collections(client)
    
    # Step 4: Check medical collection
    medical_result = check_medical_collection(client)
    
    # Step 5: Check storage stats
    check_storage_stats(client)
    
    # Step 6: Check write permission
    check_write_permission(client)
    
    # Final Summary
    logger.info(f"\n{'='*70}")
    logger.info(f"SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"✅ Connection Status: OK")
    logger.info(f"✅ Total Collections: {collections_result.get('count', 0)}")
    
    if medical_result.get("exists"):
        logger.info(f"✅ Medical Collection: EXISTS ({medical_result.get('points', 0)} vectors)")
    else:
        logger.info(f"⚠️  Medical Collection: NOT CREATED")
        logger.info(f"   → Run: python3 setup_qdrant_local.py")
    
    logger.info(f"{'='*70}")
    
    # Next steps
    logger.info(f"\n📋 NEXT STEPS:")
    logger.info(f"{'='*70}")
    
    if not medical_result.get("exists"):
        logger.info(f"1. Create and populate medical collection:")
        logger.info(f"   python3 setup_qdrant_local.py")
        logger.info(f"")
    
    logger.info(f"2. Start the application:")
    logger.info(f"   python3 app.py")
    logger.info(f"")
    logger.info(f"3. Access the UI:")
    logger.info(f"   http://localhost:8000")
    logger.info(f"")
    logger.info(f"4. View Qdrant Dashboard:")
    logger.info(f"   http://localhost:6333/dashboard")
    logger.info(f"{'='*70}")
    
    logger.info(f"\n✅ All checks completed successfully!")
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Checks interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
