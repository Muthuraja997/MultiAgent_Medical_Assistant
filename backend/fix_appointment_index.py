"""
Script to fix the duplicate key error by dropping the incorrect appointment_id index
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def fix_appointment_index():
    """Drop the problematic appointment_id unique index"""
    try:
        # MongoDB Atlas connection
        MONGODB_URI = "mongodb+srv://muthu_user:Muthu93@cluster0.b69bba9.mongodb.net/"
        DATABASE_NAME = "medical_assistant_db"
        
        # Connect to MongoDB
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
