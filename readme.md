# The FollowUp Agency Onboarding Project

## Introduction

Welcome to the **The FollowUp Agency Onboarding Project**! This project serves as an API for making autonomous web automations. It is designed to provide web automations and third-party integrations through a set of well-defined API endpoints.

### Key Features

- **Web Automation:** Execute autonomous web automations seamlessly.
- **Third-Party Integrations:** Integrate with external services and APIs effortlessly.
- **Selenium Web Browser:** Leverage the power of the Selenium web browser for automation tasks.
- **Data Storage and Transfer:** Efficiently store and transfer data as part of your automation workflows.
- **Google Authentication System:** Securely authenticate and authorize users using Google authentication.

This README will guide you through the installation, configuration, and usage of the project, ensuring a smooth onboarding experience for developers.

# Requirements

To run The FollowUp Agency Onboarding Project, ensure that you have the following prerequisites installed:

- **Python 3.7+**
- **Django 3.0+**
- **Docker**
- **GCP account**

These requirements are essential for setting up and running the project successfully.

# Installation

To get started with The FollowUp Agency Onboarding Project, follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Ocolus1/hl-contact.git
   cd hl-contact

2. **Create a Virtual Environment:**

   ```bash
    python -m venv venv
    source venv/bin/activate  # For Windows: venv\Scripts\activate

## Install Dependencies

    pip install -r requirements.txt

1. **Set Up Docker:**
   Ensure Docker is installed and running on your machine.

2. **Configure GCP Account:**
   Create a GCP account and set up the necessary credentials.

3. **Run the Project:**

   ```bash
   python manage.py runserver

# Configuration

Before running The FollowUp Agency Onboarding Project, make sure to configure the following settings:

1. **Django Settings:**
   Open the `settings.py` file in the project directory to customize any specific configurations. Modify the file according to your project requirements.

2. **Environment Variables:**
   Create a `.env` file in the project root and set the following variables:

   ```dotenv
   TOKEN=your_jwt_token
   SECRET_KEY=your_django_secret_key
   EMAIL_PASSWORD=your_email_password
   EMAIL=your_email_address
   USER_EMAIL=your_user_email
   USER_EMAIL_PASSWORD=your_user_email_password
   CLIENT_ID=your_google_client_id
   CLIENT_SECRET=your_google_client_secret
   CALLBACK_URL=your_google_callback_url
   STRIPE_SECRET_KEY=your_stripe_secret_key
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=your_database_host
   DB_PORT=your_database_port
   ALLOWED_HOSTS=your_allowed_hosts
   DEBUG=True
   GS_PROJECT_ID=your_google_storage_project_id
   GS_BUCKET_NAME=your_google_storage_bucket_name
Adjust the values according to your environment.

3. **Google API Credentials:**

   If using Google authentication, set up and configure the Google API credentials. Store the credentials file in a secure location and reference it in your Django settings.
These configuration steps are crucial for ensuring the proper functioning of the project.

# Usage

Once The FollowUp Agency Onboarding Project is successfully set up, you can interact with its features using the provided API endpoints. Here are some key usage instructions:

1. **Run the Server:**
   Start the Django development server using the following command:
   ```bash
   python manage.py runserver

2. **Access the API Documentation:**
Open your web browser and navigate to [http://localhost:8000/docs](http://localhost:8000/docs) to access the Swagger documentation. This interactive documentation provides detailed information about available API endpoints and allows you to test them.

3. **Execute Web Automations:**
Utilize the API endpoints related to web automations to trigger autonomous processes. Follow the API documentation for specific endpoints and payload requirements.

4. **Integrate Third-Party Services:**
Leverage the API endpoints for third-party integrations to connect with external services. Check the documentation for authentication details and request payloads.

Feel free to explore and experiment with the provided API to make the most of The FollowUp Agency Onboarding Project.

# API Endpoints

The FollowUp Agency Onboarding Project provides the following API endpoints, each serving a specific functionality.


Refer to the Swagger documentation at [http://localhost:8000/docs](http://localhost:8000/docs) for detailed information on each endpoint, including request and response formats.

Feel free to explore and use these endpoints to harness the full capabilities of The FollowUp Agency Onboarding Project.


# Authentication

The FollowUp Agency Onboarding Project currently relies solely on Google authentication for secure access. To interact with the API, follow the steps below:

1. **Google Authentication:**
   - Ensure you have the required Google API credentials.
   - Set up the Google API credentials and securely store the credentials file.
   - Reference the credentials file in your Django settings for authentication.

2. **Token Authentication:**
   - For specific endpoints, authentication is necessary using a token.
   - Include the token in the request headers in the following format:
     ```
     Authorization: Bearer your_token_here
     ```

Make sure you possess the necessary Google API credentials and adhere to the provided authentication method for each endpoint. Detailed endpoint-specific authentication information is available in the Swagger documentation at [http://localhost:8000/docs](http://localhost:8000/docs).


# Conclusion

Congratulations on successfully setting up and exploring The FollowUp Agency Onboarding Project! This API provides a robust platform for autonomous web automations and seamless third-party integrations. As you continue to work with the project, feel free to refer to the detailed documentation provided here, including installation instructions, configuration details, and insights into available API endpoints.


Happy automating!
