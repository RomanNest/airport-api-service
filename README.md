# Airport-api-service

### Introduction
This is a Django-based API for tracking flights from airports.

### Technologies that were included to this project
1. **Django REST Framework**: for managing API views.
2. **PostgresSQL**: as a main database.
3. **Docker Compose**: for developing the microservices.
4. **Swagger & Redock**: for api documentation.

### Airport Service Feature
* JWT authentication
* Admin panel /admin/.
* Recording information about countries and cities, associating airports with their closest big city.
* Creating and managing routers (based on airports).
* Creating and managing airplanes and airplane types.
* Creating and managing crews.
* Creating and managing flights.
* Different types of filtering.
* The ability to upload airplane images to show a specific kind of airplane.
* Creating and managing orders made by users, including tickets with row and seat detail.

### Running with Docker
To run the project with Docker, follow these steps:
1. Clone the repository:
    ```bash
   https://github.com/RomanNest/airport-api-service.git
    ```
2. Navigate to the project directory:
    ```bash
   cd aerport-api-service
    ```
3. Build and run the Docker containers:
    ```bash
    docker-compose up --build
    ```
4. Access the API endpoints via 
    `http://localhost:8001`

### Running on Machine
To run the project on your local machine without Docker follow these steps:
1. Clone the repository:
    ```bash
   https://github.com/RomanNest/airport-api-service.git
    ```
2. Navigate to the project directory:
    ```bash
   cd aerport-api-service
    ```
3. Install the Python dependencies:
    ```bash
    pip instal -r requirements.txt
    ```
4. Apply database migrations:
    ```bash
    python manage.py migrate
    ```
5. Run the development server:
    ```bash
    python manage.py runserver
    ```
6. Access the API endpoints via
    `http://localhost:8000`

### API Endpoints
Below is a summary of the API endpoints provided by the project:
- **Crews**: `/api/airport/crews/`
- **Countries**: `/api/airport/countries/`
- **Cities**: `/api/airport/cities/`
- **Airports**: `/api/airport/airports/`
- **Airplane Types**: `/api/airport/airplane_types/`
- **Airplanes**: `/api/airport/airplanes/`
- **Routes**: `/api/airport/routes/`
- **Flights**: `/api/airport/flights/`
- **Orders**: `/api/airport/orders/`
- **Users**: `/api/user/register`,`/api/user/me` `/api/user/token`, `/api/user/token/refresh`, `/api/user/token/verify`
Each endpoint supports various operations such as listing, creation, retrieval, and updating of resources.


