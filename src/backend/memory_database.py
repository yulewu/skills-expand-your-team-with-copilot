"""
In-memory database implementation for development/testing purposes
This replaces MongoDB functionality when MongoDB is not available.
"""

from argon2 import PasswordHasher
from typing import Dict, Any, List, Optional
import copy

# In-memory storage
_activities_store: Dict[str, Any] = {}
_teachers_store: Dict[str, Any] = {}

class MemoryCollection:
    """Mock MongoDB collection using in-memory dictionary"""
    
    def __init__(self, store: Dict[str, Any]):
        self.store = store
    
    def find_one(self, query: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        if not query:
            if self.store:
                first_key = next(iter(self.store))
                result = copy.deepcopy(self.store[first_key])
                result['_id'] = first_key
                return result
            return None
        
        if '_id' in query:
            key = query['_id']
            if key in self.store:
                result = copy.deepcopy(self.store[key])
                result['_id'] = key
                return result
            return None
        
        # For more complex queries, iterate through all items
        for key, value in self.store.items():
            if self._matches_query(value, query):
                result = copy.deepcopy(value)
                result['_id'] = key
                return result
        return None
    
    def find(self, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        results = []
        for key, value in self.store.items():
            if not query or self._matches_query(value, query):
                result = copy.deepcopy(value)
                result['_id'] = key
                results.append(result)
        return results
    
    def insert_one(self, document: Dict[str, Any]):
        key = document.pop('_id')
        self.store[key] = copy.deepcopy(document)
        return type('InsertResult', (), {'inserted_id': key})()
    
    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]):
        if '_id' in query:
            key = query['_id']
            if key in self.store:
                if '$push' in update:
                    for field, value in update['$push'].items():
                        if field not in self.store[key]:
                            self.store[key][field] = []
                        self.store[key][field].append(value)
                if '$pull' in update:
                    for field, value in update['$pull'].items():
                        if field in self.store[key]:
                            self.store[key][field] = [x for x in self.store[key][field] if x != value]
                return type('UpdateResult', (), {'modified_count': 1})()
        return type('UpdateResult', (), {'modified_count': 0})()
    
    def count_documents(self, query: Dict[str, Any] = None) -> int:
        if not query:
            return len(self.store)
        return len(self.find(query))
    
    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Simple aggregation support for getting unique days
        results = []
        for operation in pipeline:
            if '$unwind' in operation:
                # Handle unwinding days array
                field = operation['$unwind'].replace('$', '')
                for key, value in self.store.items():
                    if field in value:
                        for item in value[field]:
                            result = copy.deepcopy(value)
                            # Set the unwound field to single value
                            keys = field.split('.')
                            current = result
                            for k in keys[:-1]:
                                current = current[k]
                            current[keys[-1]] = item
                            result['_id'] = key
                            results.append(result)
            elif '$group' in operation:
                # Handle grouping
                group_key = operation['$group']['_id'].replace('$', '')
                unique_values = set()
                for result in results:
                    keys = group_key.split('.')
                    current = result
                    for k in keys:
                        if k in current:
                            current = current[k]
                        else:
                            current = None
                            break
                    if current is not None:
                        unique_values.add(current)
                results = [{'_id': value} for value in sorted(unique_values)]
            elif '$sort' in operation:
                # Handle sorting
                sort_field = list(operation['$sort'].keys())[0]
                results.sort(key=lambda x: x.get(sort_field, ''))
        
        return results
    
    def _matches_query(self, document: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """Check if document matches query"""
        for key, expected in query.items():
            if isinstance(expected, dict):
                if '$in' in expected:
                    # Handle $in operator for array fields
                    if key not in document:
                        return False
                    if not isinstance(document[key], list):
                        return False
                    if not any(item in expected['$in'] for item in document[key]):
                        return False
                elif '$gte' in expected:
                    if key not in document:
                        return False
                    if document[key] < expected['$gte']:
                        return False
                elif '$lte' in expected:
                    if key not in document:
                        return False
                    if document[key] > expected['$lte']:
                        return False
                elif '$exists' in expected:
                    # Handle $exists operator
                    exists = key in document
                    if expected['$exists'] != exists:
                        return False
            else:
                if key not in document:
                    return False
                if document[key] != expected:
                    return False
        return True

# Create mock collections
activities_collection = MemoryCollection(_activities_store)
teachers_collection = MemoryCollection(_teachers_store)

# Methods
def hash_password(password):
    """Hash password using Argon2"""
    ph = PasswordHasher()
    return ph.hash(password)

def init_database():
    """Initialize database if empty"""
    
    # Initialize activities if empty
    if activities_collection.count_documents({}) == 0:
        for name, details in initial_activities.items():
            activities_collection.insert_one({"_id": name, **details})
            
    # Initialize teacher accounts if empty
    if teachers_collection.count_documents({}) == 0:
        for teacher in initial_teachers:
            teachers_collection.insert_one({"_id": teacher["username"], **teacher})

# Updated initial activities with difficulty levels
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Mondays and Fridays, 3:15 PM - 4:45 PM",
        "schedule_details": {
            "days": ["Monday", "Friday"],
            "start_time": "15:15",
            "end_time": "16:45"
        },
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        "difficulty": "Beginner"
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 7:00 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "07:00",
            "end_time": "08:00"
        },
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        "difficulty": "Intermediate"
    },
    "Morning Fitness": {
        "description": "Early morning physical training and exercises",
        "schedule": "Mondays, Wednesdays, Fridays, 6:30 AM - 7:45 AM",
        "schedule_details": {
            "days": ["Monday", "Wednesday", "Friday"],
            "start_time": "06:30",
            "end_time": "07:45"
        },
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        "difficulty": "Beginner"
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Tuesday", "Thursday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
        "difficulty": "Intermediate"
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball tournaments",
        "schedule": "Wednesdays and Fridays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Wednesday", "Friday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
        "difficulty": "Intermediate"
    },
    "Art Club": {
        "description": "Explore various art techniques and create masterpieces",
        "schedule": "Thursdays, 3:15 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Thursday"],
            "start_time": "15:15",
            "end_time": "17:00"
        },
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
        "difficulty": "Beginner"
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Monday", "Wednesday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
        "difficulty": "Intermediate"
    },
    "Math Club": {
        "description": "Solve challenging problems and prepare for math competitions",
        "schedule": "Tuesdays, 7:15 AM - 8:00 AM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "07:15",
            "end_time": "08:00"
        },
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
        "difficulty": "Advanced"
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 3:30 PM - 5:30 PM",
        "schedule_details": {
            "days": ["Friday"],
            "start_time": "15:30",
            "end_time": "17:30"
        },
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "amelia@mergington.edu"],
        "difficulty": "Advanced"
    },
    "Weekend Robotics Workshop": {
        "description": "Build and program robots in our state-of-the-art workshop",
        "schedule": "Saturdays, 10:00 AM - 2:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "10:00",
            "end_time": "14:00"
        },
        "max_participants": 15,
        "participants": ["ethan@mergington.edu", "oliver@mergington.edu"],
        "difficulty": "Advanced"
    },
    "Science Olympiad": {
        "description": "Weekend science competition preparation for regional and state events",
        "schedule": "Saturdays, 1:00 PM - 4:00 PM",
        "schedule_details": {
            "days": ["Saturday"],
            "start_time": "13:00",
            "end_time": "16:00"
        },
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"],
        "difficulty": "Advanced"
    },
    "Sunday Chess Tournament": {
        "description": "Weekly tournament for serious chess players with rankings",
        "schedule": "Sundays, 2:00 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Sunday"],
            "start_time": "14:00",
            "end_time": "17:00"
        },
        "max_participants": 16,
        "participants": ["william@mergington.edu", "jacob@mergington.edu"],
        "difficulty": "Advanced"
    },
    # Activities without difficulty level (for "All" filter)
    "Manga Maniacs": {
        "description": "Explore the fantastic stories of the most interesting characters from Japanese Manga (graphic novels).",
        "schedule": "Tuesdays, 7:00 PM - 8:00 PM",
        "schedule_details": {
            "days": ["Tuesday"],
            "start_time": "19:00",
            "end_time": "20:00"
        },
        "max_participants": 15,
        "participants": []
        # No difficulty field - this is intentional for the "All" filter
    },
    "Student Council": {
        "description": "Represent your fellow students and organize school events",
        "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
        "schedule_details": {
            "days": ["Wednesday"],
            "start_time": "16:00",
            "end_time": "17:00"
        },
        "max_participants": 12,
        "participants": ["sarah@mergington.edu"]
        # No difficulty field - this is intentional for the "All" filter
    }
}

initial_teachers = [
    {
        "username": "mrodriguez",
        "display_name": "Ms. Rodriguez",
        "password": hash_password("art123"),
        "role": "teacher"
     },
    {
        "username": "mchen",
        "display_name": "Mr. Chen",
        "password": hash_password("chess456"),
        "role": "teacher"
    },
    {
        "username": "principal",
        "display_name": "Principal Martinez",
        "password": hash_password("admin789"),
        "role": "admin"
    }
]