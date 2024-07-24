from app import create_app, db

def main():
    app = create_app()  # Initialize your Flask application

    with app.app_context():  # Use the application context
        db.create_all()  # Create tables defined in your models
        print("Tables created successfully")

if __name__ == "__main__":
    main()
