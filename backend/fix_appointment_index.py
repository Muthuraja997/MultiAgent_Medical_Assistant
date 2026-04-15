"""
Script to fix the duplicate key error by dropping the incorrect appointment_id index
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

_backend_root = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_backend_root, ".env"))
load_dotenv()


async def fix_appointment_index():
    """Drop the problematic appointment_id unique index"""
    try:
        MONGODB_URI = os.getenv("MONGODB_URI")
        DATABASE_NAME = os.getenv("DATABASE_NAME", "medical_assistant_db")

        if not MONGODB_URI:
            raise ValueError(
                "MONGODB_URI is not set. Add it to backend/.env (or export it) and retry."
            )
        if not MONGODB_URI.startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("MONGODB_URI must start with mongodb:// or mongodb+srv://")

        client = AsyncIOMotorClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        
        print("Connected to MongoDB")
        
        # List all indexes on appointments collection
        print("\n📋 Current indexes on 'appointments' collection:")
        indexes = await db.appointments.index_information()
        for index_name, index_info in indexes.items():
            print(f"  - {index_name}: {index_info}")
        
        # Drop the appointment_id index if it exists
        if "appointment_id_1" in indexes:
            print("\n🔧 Dropping 'appointment_id_1' index...")
            await db.appointments.drop_index("appointment_id_1")
            print("✅ Successfully dropped 'appointment_id_1' index")
        else:
            print("\n⚠️  'appointment_id_1' index not found")
        
        # List indexes again to confirm
        print("\n📋 Updated indexes on 'appointments' collection:")
        indexes = await db.appointments.index_information()
        for index_name, index_info in indexes.items():
            print(f"  - {index_name}: {index_info}")
        
        # Close connection
        client.close()
        print("\n✅ Index fix completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(fix_appointment_index())
