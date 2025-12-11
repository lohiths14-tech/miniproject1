"""
Simple MongoDB Atlas Connection and Database Initialization
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_and_initialize():
    """Test connection and initialize database"""

    print("=" * 70)
    print("🚀 MongoDB Atlas Setup & Initialization")
    print("=" * 70)

    try:
        # Get connection string
        mongo_uri = os.getenv('MONGO_URI')

        if not mongo_uri:
            print("\n❌ MONGO_URI not found in .env file")
            return False

        print("\n📡 Connecting to MongoDB Atlas...")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)

        # Test connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")

        # Get database
        db = client.get_database()
        print(f"\n📊 Database: {db.name}")

        print("\n🔨 Creating indexes for optimal performance...")

        # Define indexes for each collection
        indexes_config = {
            'users': [
                ('email', {'unique': True}),
                ('role', {}),
            ],
            'assignments': [
                ('course_id', {}),
                ('created_at', {}),
            ],
            'submissions': [
                ('assignment_id', {}),
                ('user_id', {}),
                ('submitted_at', {}),
            ],
            'gamification': [
                ('user_id', {'unique': True}),
                ('total_points', {}),
            ],
            'courses': [
                ('code', {'unique': True}),
            ],
        }

        # Create indexes
        total_indexes = 0
        for collection_name, index_list in indexes_config.items():
            collection = db[collection_name]

            for field, options in index_list:
                try:
                    collection.create_index(field, **options)
                    unique = " (unique)" if options.get('unique') else ""
                    print(f"   ✅ {collection_name}.{field}{unique}")
                    total_indexes += 1
                except Exception as e:
                    if "already exists" not in str(e):
                        print(f"   ⚠️  {collection_name}.{field}: {str(e)[:50]}")

        print(f"\n📈 Created/verified {total_indexes} indexes")

        # Show collections
        collections = db.list_collection_names()
        print(f"\n📁 Collections ({len(collections)}):")
        if collections:
            for col in sorted(collections):
                count = db[col].count_documents({})
                print(f"   - {col}: {count} documents")
        else:
            print("   (No collections yet)")

        # Get server info
        server_info = client.server_info()
        print(f"\n🖥️  Server: MongoDB {server_info.get('version')}")

        print("\n" + "=" * 70)
        print("✨ Database setup completed successfully!")
        print("=" * 70)
        print("\n🎉 Your AI Grading System is now connected to MongoDB Atlas!")
        print("🚀 You can now start your application with: python app.py")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your MONGO_URI in .env file")
        print("   2. Verify your IP is whitelisted in MongoDB Atlas")
        print("   3. Confirm username and password are correct")
        return False

if __name__ == "__main__":
    success = test_and_initialize()
    exit(0 if success else 1)
