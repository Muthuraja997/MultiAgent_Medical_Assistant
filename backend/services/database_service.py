"""
Database Service

Handles all database operations for MongoDB.
Uses Motor (async MongoDB driver) for FastAPI compatibility.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from services.auth_service import auth_service


class DatabaseManager:
    """Manages MongoDB connections and operations"""
    
    def __init__(self, mongodb_uri: str, database_name: str):
        """Initialize database manager"""
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect_async(self):
        """Establish connection to MongoDB"""
        self.client = AsyncIOMotorClient(self.mongodb_uri)
        self.db = self.client[self.database_name]
        print(f"✅ Connected to MongoDB: {self.database_name}")
    
    async def close_async(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔒 MongoDB connection closed")
    
    # ==================== AUTHENTICATION ====================
    
    async def login_user(self, user_id: str, password: str, user_type: str) -> Optional[Dict[str, Any]]:
        """Authenticate user or doctor"""
        if user_type == "USER":
            user = await self.db.users.find_one({"user_id": user_id})
            if user and auth_service.verify_password(password, user.get("password", "")):
                return user
        elif user_type == "DOCTOR":
            doctor = await self.db.doctors.find_one({"doctor_id": user_id})
            if doctor and auth_service.verify_password(password, doctor.get("password", "")):
                return doctor
        return None
    
    async def register_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Register a new user or doctor"""
        user_type = user_data.get("user_type")
        
        if user_type == "USER":
            # Check if user_id already exists
            existing = await self.db.users.find_one({"user_id": user_data["user_id"]})
            if existing:
                return None
            
            # Create user document
            user_doc = {
                "user_id": user_data["user_id"],
                "user_name": user_data["name"],
                "user_type": "USER",
                "appointment_status": "SCHEDULED",
                "doctor_id": None,
                "password": auth_service.hash_password(user_data["password"]),
                "email": user_data.get("email"),
                "phone": user_data.get("phone"),
                "created_at": datetime.utcnow()
            }
            await self.db.users.insert_one(user_doc)
            return user_doc
            
        elif user_type == "DOCTOR":
            # Check if doctor_id already exists
            existing = await self.db.doctors.find_one({"doctor_id": user_data["user_id"]})
            if existing:
                return None
            
            # Create doctor document
            doctor_doc = {
                "doctor_id": user_data["user_id"],
                "doc_name": user_data["name"],
                "available_status": True,
                "password": auth_service.hash_password(user_data["password"]),
                "email": user_data.get("email"),
                "phone": user_data.get("phone"),
                "created_at": datetime.utcnow()
            }
            await self.db.doctors.insert_one(doctor_doc)
            return doctor_doc
        
        return None
    
    # ==================== USER OPERATIONS ====================
    
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        # Hash password before storing
        user_data["password"] = auth_service.hash_password(user_data["password"])
        user_data["created_at"] = datetime.utcnow()
        result = await self.db.users.insert_one(user_data)
        return str(result.inserted_id)
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        user = await self.db.users.find_one({"user_id": user_id})
        if user:
            # Remove password from response
            user.pop("password", None)
        return user
    
    async def get_all_users(self, user_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all users, optionally filtered by type"""
        query = {"user_type": user_type} if user_type else {}
        cursor = self.db.users.find(query)
        users = await cursor.to_list(length=None)
        # Remove passwords
        for user in users:
            user.pop("password", None)
        return users
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user information"""
        # Hash password if it's being updated
        if "password" in update_data:
            update_data["password"] = auth_service.hash_password(update_data["password"])
        
        update_data["updated_at"] = datetime.utcnow()
        result = await self.db.users.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        result = await self.db.users.delete_one({"user_id": user_id})
        return result.deleted_count > 0
    
    # ==================== DOCTOR OPERATIONS ====================
    
    async def create_doctor(self, doctor_data: Dict[str, Any]) -> str:
        """Create a new doctor"""
        # Hash password before storing
        doctor_data["password"] = auth_service.hash_password(doctor_data["password"])
        doctor_data["created_at"] = datetime.utcnow()
        result = await self.db.doctors.insert_one(doctor_data)
        return str(result.inserted_id)
    
    async def get_doctor(self, doctor_id: str) -> Optional[Dict[str, Any]]:
        """Get doctor by ID"""
        doctor = await self.db.doctors.find_one({"doctor_id": doctor_id})
        if doctor:
            # Remove password from response
            doctor.pop("password", None)
        return doctor
    
    async def get_all_doctors(self, available_only: bool = False) -> List[Dict[str, Any]]:
        """Get all doctors, optionally only available ones"""
        query = {"available_status": True} if available_only else {}
        cursor = self.db.doctors.find(query)
        doctors = await cursor.to_list(length=None)
        # Remove passwords
        for doctor in doctors:
            doctor.pop("password", None)
        return doctors
    
    async def update_doctor(self, doctor_id: str, update_data: Dict[str, Any]) -> bool:
        """Update doctor information"""
        # Hash password if it's being updated
        if "password" in update_data:
            update_data["password"] = auth_service.hash_password(update_data["password"])
        
        update_data["updated_at"] = datetime.utcnow()
        result = await self.db.doctors.update_one(
            {"doctor_id": doctor_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def update_doctor_availability(self, doctor_id: str, available: bool) -> bool:
        """Update doctor availability status"""
        result = await self.db.doctors.update_one(
            {"doctor_id": doctor_id},
            {"$set": {"available_status": available, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    async def delete_doctor(self, doctor_id: str) -> bool:
        """Delete a doctor"""
        result = await self.db.doctors.delete_one({"doctor_id": doctor_id})
        return result.deleted_count > 0
    
    # ==================== MEETING OPERATIONS ====================
    
    async def create_meeting(self, meeting_data: Dict[str, Any]) -> str:
        """Create a new meeting"""
        meeting_data["created_at"] = datetime.utcnow()
        result = await self.db.meetings.insert_one(meeting_data)
        return str(result.inserted_id)
    
    async def get_meeting(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Get meeting by ID"""
        return await self.db.meetings.find_one({"_id": ObjectId(meeting_id)})
    
    async def get_doctor_meetings(self, doctor_id: str) -> List[Dict[str, Any]]:
        """Get all meetings for a doctor"""
        cursor = self.db.meetings.find({"doctor_id": doctor_id})
        return await cursor.to_list(length=None)
    
    async def get_all_meetings(self) -> List[Dict[str, Any]]:
        """Get all meetings"""
        cursor = self.db.meetings.find({})
        return await cursor.to_list(length=None)
    
    async def update_meeting(self, meeting_id: str, update_data: Dict[str, Any]) -> bool:
        """Update meeting information"""
        update_data["updated_at"] = datetime.utcnow()
        result = await self.db.meetings.update_one(
            {"_id": ObjectId(meeting_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting"""
        result = await self.db.meetings.delete_one({"_id": ObjectId(meeting_id)})
        return result.deleted_count > 0
    
    # ==================== APPOINTMENT REQUEST OPERATIONS ====================
    
    async def create_appointment_request(self, user_id: str, user_name: str, request_data: Dict[str, Any]) -> str:
        """Create a new appointment request"""
        request_doc = {
            "user_id": user_id,
            "user_name": user_name,
            "doctor_id": request_data["doctor_id"],
            "reason": request_data.get("reason"),
            "preferred_date": request_data.get("preferred_date"),
            "preferred_time": request_data.get("preferred_time"),
            "status": "PENDING",
            "created_at": datetime.utcnow()
        }
        result = await self.db.appointments.insert_one(request_doc)
        return str(result.inserted_id)
    
    async def get_appointment_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get appointment request by ID"""
        return await self.db.appointments.find_one({"_id": ObjectId(request_id)})
    
    async def get_doctor_appointment_requests(self, doctor_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all appointment requests for a doctor"""
        query = {"doctor_id": doctor_id}
        if status:
            query["status"] = status
        cursor = self.db.appointments.find(query).sort("created_at", -1)
        return await cursor.to_list(length=None)
    
    async def get_user_appointment_requests(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all appointment requests for a user"""
        cursor = self.db.appointments.find({"user_id": user_id}).sort("created_at", -1)
        return await cursor.to_list(length=None)
    
    async def update_appointment_request(self, request_id: str, status: str, meet_link: Optional[str] = None) -> Dict[str, Any]:
        """Update appointment request status and create meeting if accepted"""
        # Get the appointment request details
        request = await self.get_appointment_request(request_id)
        if not request:
            return {"success": False, "message": "Appointment request not found"}
        
        # If accepting, create Jitsi meeting automatically
        if status == "ACCEPTED":
            # Generate unique Jitsi room name
            import random
            import string
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            room_name = f"medical-consult-{timestamp}-{random_id}"
            meet_link = f"https://meet.jit.si/{room_name}"
            
            # Get doctor and user details
            doctor = await self.get_doctor(request["doctor_id"])
            user = await self.get_user(request["user_id"])
            
            # Create meeting record in meetings collection
            meeting_doc = {
                "appointment_id": str(request["_id"]),
                "room_name": room_name,
                "meet_link": meet_link,
                "doctor_id": request["doctor_id"],
                "doctor_name": doctor.get("doc_name") if doctor else "Unknown Doctor",
                "user_id": request["user_id"],
                "user_name": request.get("user_name", user.get("user_name") if user else "Unknown User"),
                "scheduled_time": request.get("preferred_date", "") + " " + request.get("preferred_time", ""),
                "reason": request.get("reason"),
                "status": "scheduled",
                "created_at": datetime.utcnow()
            }
            
            meeting_result = await self.db.meetings.insert_one(meeting_doc)
            meeting_id = str(meeting_result.inserted_id)
            
            # Update appointment with meeting link and meeting_id
            update_data = {
                "status": status,
                "meet_link": meet_link,
                "meeting_id": meeting_id,
                "updated_at": datetime.utcnow()
            }
        else:
            # For reject or other status updates
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            if meet_link:
                update_data["meet_link"] = meet_link
        
        result = await self.db.appointments.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": update_data}
        )
        
        # If accepted, update doctor availability to busy
        if status == "ACCEPTED" and result.modified_count > 0:
            await self.update_doctor_availability(request["doctor_id"], False)
        
        if result.modified_count > 0:
            return {
                "success": True,
                "message": "Appointment updated successfully",
                "meet_link": update_data.get("meet_link"),
                "meeting_id": update_data.get("meeting_id") if status == "ACCEPTED" else None
            }
        else:
            return {"success": False, "message": "Failed to update appointment"}
    
    async def get_meeting(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Get meeting by ID"""
        return await self.db.meetings.find_one({"_id": ObjectId(meeting_id)})
    
    async def get_user_meetings(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all meetings for a user"""
        cursor = self.db.meetings.find({"user_id": user_id}).sort("created_at", -1)
        return await cursor.to_list(length=None)
    
    async def get_doctor_meetings(self, doctor_id: str) -> List[Dict[str, Any]]:
        """Get all meetings for a doctor"""
        cursor = self.db.meetings.find({"doctor_id": doctor_id}).sort("created_at", -1)
        return await cursor.to_list(length=None)
    
    # ==================== STATISTICS ====================
    
    async def get_statistics(self) -> Dict[str, int]:
        """Get platform statistics"""
        total_users = await self.db.users.count_documents({})
        total_doctors = await self.db.doctors.count_documents({})
        available_doctors = await self.db.doctors.count_documents({"available_status": True})
        total_meetings = await self.db.meetings.count_documents({})
        total_appointment_requests = await self.db.appointments.count_documents({})
        
        return {
            "total_users": total_users,
            "total_doctors": total_doctors,
            "available_doctors": available_doctors,
            "total_meetings": total_meetings,
            "total_appointment_requests": total_appointment_requests
        }


# MongoDB Configuration
MONGODB_URI = "mongodb+srv://muthu_user:Muthu93@cluster0.b69bba9.mongodb.net/"
DATABASE_NAME = "medical_assistant_db"

# Global database manager instance
db_manager = DatabaseManager(MONGODB_URI, DATABASE_NAME)
