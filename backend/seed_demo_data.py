"""
Seed script for demo data - Creates test users, vehicles, and routes

This script populates the database with realistic demo data for hackathon presentation:
- Test riders with pre-created accounts
- Test drivers with vehicles
- Active routes for demonstration
- No registration needed - just login and test!

Run this script after starting the backend:
    python seed_demo_data.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from datetime import datetime, timedelta
from src.config.database import SessionLocal, init_db
from src.models.user import User, UserRole
from src.models.vehicle import Vehicle
from src.models.route import Route, RouteStatus
from src.utils.auth import hash_password

def clear_database(db):
    """Clear existing data for fresh demo"""
    print("🗑️  Clearing existing demo data...")
    db.query(Route).delete()
    db.query(Vehicle).delete()
    db.query(User).delete()
    db.commit()
    print("✅ Database cleared")

def create_test_users(db):
    """Create test rider and driver accounts"""
    print("\n👥 Creating test users...")
    
    # Test password for all demo accounts (hashed)
    test_password = hash_password("demo123")
    
    users = [
        # Riders
        User(
            email="rider@demo.com",
            password=test_password,
            name="Demo Rider",
            phone="08012345678",
            role=UserRole.RIDER
        ),
        User(
            email="john@test.com",
            password=test_password,
            name="John Doe",
            phone="08023456789",
            role=UserRole.RIDER
        ),
        User(
            email="sarah@test.com",
            password=test_password,
            name="Sarah Williams",
            phone="08034567890",
            role=UserRole.RIDER
        ),
        
        # Drivers
        User(
            email="driver@demo.com",
            password=test_password,
            name="Demo Driver",
            phone="08087654321",
            role=UserRole.DRIVER
        ),
        User(
            email="mike@driver.com",
            password=test_password,
            name="Mike Johnson",
            phone="08076543210",
            role=UserRole.DRIVER
        ),
        User(
            email="ada@driver.com",
            password=test_password,
            name="Ada Okafor",
            phone="08065432109",
            role=UserRole.DRIVER
        ),
    ]
    
    db.add_all(users)
    db.commit()
    
    print(f"✅ Created {len(users)} test users:")
    print("\n   RIDERS (Login with these):")
    print("   📧 rider@demo.com  | Password: demo123")
    print("   📧 john@test.com   | Password: demo123")
    print("   📧 sarah@test.com  | Password: demo123")
    print("\n   DRIVERS (Login with these):")
    print("   📧 driver@demo.com | Password: demo123")
    print("   📧 mike@driver.com | Password: demo123")
    print("   📧 ada@driver.com  | Password: demo123")
    
    return users

def create_test_vehicles(db, drivers):
    """Create vehicles for test drivers"""
    print("\n🚗 Creating test vehicles...")
    
    vehicles = [
        Vehicle(
            driver_id=drivers[0].id,  # Demo Driver
            make="Toyota",
            model="Hiace",
            year=2020,
            color="White",
            plate_number="LAG-123-XY",
            capacity=14
        ),
        Vehicle(
            driver_id=drivers[1].id,  # Mike Johnson
            make="Toyota",
            model="Corolla",
            year=2019,
            color="Silver",
            plate_number="ABJ-456-ZZ",
            capacity=4
        ),
        Vehicle(
            driver_id=drivers[2].id,  # Ada Okafor
            make="Honda",
            model="Civic",
            year=2021,
            color="Black",
            plate_number="LAG-789-AB",
            capacity=4
        ),
    ]
    
    db.add_all(vehicles)
    db.commit()
    
    print(f"✅ Created {len(vehicles)} vehicles")
    return vehicles

def create_test_routes(db, drivers, vehicles):
    """Create active routes for demonstration"""
    print("\n🛣️  Creating test routes...")
    
    tomorrow = datetime.now().date() + timedelta(days=1)
    
    routes = [
        # Route 1: Popular mainland route
        Route(
            driver_id=drivers[0].id,
            vehicle_id=vehicles[0].id,
            start_location="Ikeja",
            end_location="VI",
            departure_date=tomorrow,
            departure_time="08:00",
            price_per_seat=1500.00,
            available_seats=12,
            total_seats=14,
            status=RouteStatus.ACTIVE,
            bus_stops=["Ikeja", "Oshodi", "Obalende", "VI"]
        ),
        
        # Route 2: Island route
        Route(
            driver_id=drivers[0].id,
            vehicle_id=vehicles[0].id,
            start_location="Lekki",
            end_location="Marina",
            departure_date=tomorrow,
            departure_time="09:00",
            price_per_seat=1200.00,
            available_seats=10,
            total_seats=14,
            status=RouteStatus.ACTIVE,
            bus_stops=["Lekki", "Ajah", "Ikoyi", "Marina"]
        ),
        
        # Route 3: Morning commute
        Route(
            driver_id=drivers[1].id,
            vehicle_id=vehicles[1].id,
            start_location="Surulere",
            end_location="Yaba",
            departure_date=tomorrow,
            departure_time="07:30",
            price_per_seat=800.00,
            available_seats=3,
            total_seats=4,
            status=RouteStatus.ACTIVE,
            bus_stops=["Surulere", "Yaba"]
        ),
        
        # Route 4: Cross-town route
        Route(
            driver_id=drivers[1].id,
            vehicle_id=vehicles[1].id,
            start_location="Ogba",
            end_location="Lekki",
            departure_date=tomorrow,
            departure_time="10:00",
            price_per_seat=2000.00,
            available_seats=4,
            total_seats=4,
            status=RouteStatus.ACTIVE,
            bus_stops=["Ogba", "Ikeja", "Obalende", "Ikoyi", "Lekki"]
        ),
        
        # Route 5: Evening route
        Route(
            driver_id=drivers[2].id,
            vehicle_id=vehicles[2].id,
            start_location="VI",
            end_location="Ikeja",
            departure_date=tomorrow,
            departure_time="17:00",
            price_per_seat=1800.00,
            available_seats=4,
            total_seats=4,
            status=RouteStatus.ACTIVE,
            bus_stops=["VI", "Obalende", "Oshodi", "Ikeja"]
        ),
        
        # Route 6: Festac to Island
        Route(
            driver_id=drivers[2].id,
            vehicle_id=vehicles[2].id,
            start_location="Festac",
            end_location="Ikoyi",
            departure_date=tomorrow,
            departure_time="08:30",
            price_per_seat=1600.00,
            available_seats=3,
            total_seats=4,
            status=RouteStatus.ACTIVE,
            bus_stops=["Festac", "Oshodi", "Obalende", "Ikoyi"]
        ),
    ]
    
    db.add_all(routes)
    db.commit()
    
    print(f"✅ Created {len(routes)} active routes")
    print("\n   Available routes for testing:")
    for i, route in enumerate(routes, 1):
        print(f"   {i}. {route.start_location} → {route.end_location} at {route.departure_time} (₦{route.price_per_seat})")
    
    return routes

def main():
    """Main seeding function"""
    print("=" * 60)
    print("🌱 OPENSEAT DEMO DATA SEEDER")
    print("=" * 60)
    
    # Initialize database
    print("\n📦 Initializing database...")
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Clear existing data
        clear_database(db)
        
        # Create users
        users = create_test_users(db)
        
        # Separate riders and drivers
        riders = [u for u in users if u.role == UserRole.RIDER]
        drivers = [u for u in users if u.role == UserRole.DRIVER]
        
        # Create vehicles for drivers
        vehicles = create_test_vehicles(db, drivers)
        
        # Create routes
        routes = create_test_routes(db, drivers, vehicles)
        
        print("\n" + "=" * 60)
        print("✅ DEMO DATA SEEDED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\n🚀 Quick Start Guide:")
        print("\n1. Start the backend:")
        print("   uvicorn main:app --reload")
        
        print("\n2. Login as RIDER:")
        print("   Email: rider@demo.com")
        print("   Password: demo123")
        
        print("\n3. Login as DRIVER:")
        print("   Email: driver@demo.com")
        print("   Password: demo123")
        
        print("\n4. Test Interswitch Payment:")
        print("   Card: 5060990580000217499")
        print("   CVV: 123")
        print("   PIN: 1234")
        
        print("\n5. Test Locations:")
        print("   Search: Ikeja → VI")
        print("   Or: Ogba → Lekki")
        print("   Or: Festac → Ikoyi")
        
        print("\n📊 Database Stats:")
        print(f"   Total Users: {len(users)} ({len(riders)} riders, {len(drivers)} drivers)")
        print(f"   Total Vehicles: {len(vehicles)}")
        print(f"   Total Routes: {len(routes)}")
        
        print("\n🎯 Demo Ready! No database setup required!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
