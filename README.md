# Employee Management System

A desktop Employee Management System built with Python and CustomTkinter, designed with Object-Oriented Programming principles and a clean modular architecture.

## Overview

Employee Management System is a desktop application for managing employee records through a graphical user interface.

The project was built to demonstrate practical Python development, Object-Oriented Programming, GUI development, data validation, exception handling, and modular application architecture.

## Features

- Employee management
- Add new employees
- Update employee information
- View employee details
- Employee status management
- Full-time and part-time employees
- Remote work profiles
- Gross salary calculation
- Tax calculation
- Input validation
- Custom exception handling
- Dark / Light appearance mode
- Custom application theme
- Splash screen
- Modular GUI architecture

## OOP Concepts

The project applies the main Object-Oriented Programming concepts:

- Encapsulation
- Abstraction
- Inheritance
- Polymorphism

The application uses an abstract `Employee` base class with specialized employee subclasses.

## Project Structure

```text
EmployeeManagementSystem/
│
├── backend/
│   ├── employee.py
│   ├── employee_operations.py
│   ├── enums.py
│   ├── exceptions.py
│   ├── full_time_employee.py
│   ├── part_time_employee.py
│   ├── remote_work_profile.py
│   └── tax_calculator.py
│
├── frontend/
│   ├── views/
│   │   ├── components/
│   │   ├── dashboard_view.py
│   │   ├── employees_view.py
│   │   └── settings_view.py
│   │
│   ├── icon/
│   ├── app.py
│   └── houda_theme.json
│
├── test/
│   └── test_full_project.py
│
├── employee_manager.py
├── main.py
├── EmployeeManagementSystem.spec
├── requirements.txt
└── Excalidraw.png
```

## Technologies

- Python
- CustomTkinter
- Pillow
- Tkinter
- Object-Oriented Programming
- PyInstaller
- unittest

## Requirements

- Python 3.x

## Getting Started

### Running from Source

1. Clone the repository:

   ```bash
   git clone https://github.com/ehoda9/EmployeeManagementSystem.git
   ```

2. Move into the project directory:

   ```bash
   cd EmployeeManagementSystem
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   python main.py
   ```

### Building the Executable

The project includes a PyInstaller specification file. Build the standalone executable with:

```bash
pyinstaller --clean --noconfirm EmployeeManagementSystem.spec
```

The final executable will be generated in:

```text
dist/EmployeeManagementSystem.exe
```

## Testing

Run the test suite with:

```bash
python -m unittest discover -s test
```

## Architecture

The project is separated into backend and frontend layers.

### Backend

Responsible for:

- Employee models
- Business operations
- Salary calculations
- Tax calculations
- Validation
- Custom exceptions
- Employee state management

### Frontend

Responsible for:

- Application window
- Splash screen
- Dashboard
- Employee management views
- Settings
- User interaction

## License

This project is released under a custom non-commercial license. You are free to view, use, and modify it for personal and educational purposes, but selling, reselling, and any other commercial use are not permitted. See the [LICENSE](LICENSE) file for details.

## Author

**Mahmoud Mohamed**

GitHub: [@ehoda9](https://github.com/ehoda9)
