from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Ensure the instance folder exists
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    # Run the application
    app.run(debug=True, port=5000)