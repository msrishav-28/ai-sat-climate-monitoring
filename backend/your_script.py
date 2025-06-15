import ee

try:
    # Attempt to initialize with a specific project ID if known.
    # Replace 'your-google-cloud-project-id' with your actual GCP Project ID.
    # This is the project you selected or created when you first authenticated GEE.
    ee.Initialize(project='your-google-cloud-project-id') 
    print("Earth Engine initialized successfully with a project ID.")
except Exception as e:
    print(f"Initialization with project failed: {e}. Attempting interactive authentication.")
    # If initialization fails (e.g., no existing credentials or wrong project ID),
    # prompt for authentication.
    ee.Authenticate()
    ee.Initialize(project='your-google-cloud-project-id') # Initialize again after auth
    print("Earth Engine authenticated and initialized successfully.")


# Now you can use the Earth Engine API
# Example: Print a simple GEE object
try:
    image = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_044034_20200318')
    print(f"GEE Image object created: {image.getInfo()}")
except Exception as e:
    print(f"Error accessing GEE: {e}")