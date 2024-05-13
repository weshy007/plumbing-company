# Plumbing Company Reservation System

## Introduction
This is a reservation system developed using Django for a local plumbing company. The system allows users to book repairs and helps plumbers manage their appointments efficiently.

## Features
- User authentication and authorization
- Booking system for users to submit repair requests
- Plumber dashboard to view appointments and required parts
- Inventory management for parts required for repairs
- Handling of out-of-stock parts with notification system
- Admin panel for managing users, appointments, and inventory
- Email notifications for various events such as new bookings and out-of-stock alerts
- Security measures to protect user data
- Testing and debugging to ensure reliability
- Deployment instructions for hosting the application

## Installation
1. Clone the repository: `git clone https://github.com/weshy007/plumbing-company.git`

2. Install dependencies:
- Create an environment with `pipenv shell` then install depandancies with `pipenv sync`.
3. Configure settings:
- Rename `example.env` to `.env` and update the configuration variables accordingly.

## Usage
1. Run migrations: `make migrate`. 
2. Create a superuser for accessing the admin panel: `python manage.py createsuperuser`
3. Start the development server: `make serve`
4. Access the application in your web browser at `http://localhost:8000`.

## Contributing
Contributions are welcome! If you'd like to contribute to this project, please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/new-feature`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Create a new pull request.

## License
This project is licensed under the [MIT License](LICENSE).

## Contact
For any inquiries or suggestions, please contact [Waithaka Waweru](https://twitter.com/ItsWeshy) on X.

