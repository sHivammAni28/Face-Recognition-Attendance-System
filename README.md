# 🎯 Face Recognition Attendance System

A modern, AI-powered attendance management system that uses advanced facial recognition technology to automate student attendance tracking. Built with Django REST Framework and React.js, featuring real-time face detection, comprehensive analytics, and an intuitive user interface.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)
![React](https://img.shields.io/badge/React-18.2.0-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13+-orange.svg)
![DeepFace](https://img.shields.io/badge/DeepFace-0.0.79+-red.svg)

## ✨ Features

### 🔐 Authentication & User Management
- **Secure Login System** - JWT-based authentication for students and administrators
- **Role-based Access Control** - Separate dashboards for students and admins
- **User Registration** - Easy student registration with profile management

### 📸 Advanced Face Recognition
- **DeepFace Integration** - State-of-the-art facial recognition using multiple AI models
- **Real-time Face Detection** - Live webcam integration for face capture and recognition
- **Multiple Detection Backends** - OpenCV, MTCNN, and other detection algorithms
- **High Accuracy** - Configurable similarity thresholds for optimal recognition
- **Anti-spoofing** - Built-in protection against photo-based attacks

### 📊 Attendance Management
- **Automated Attendance** - One-click attendance marking via facial recognition
- **Real-time Tracking** - Instant attendance status updates
- **Session Management** - Support for multiple daily sessions (morning, afternoon, etc.)
- **Late Arrival Detection** - Automatic late marking based on configurable time windows
- **Attendance History** - Complete historical records with detailed analytics

### 📈 Analytics & Reporting
- **Interactive Dashboards** - Comprehensive admin and student dashboards
- **Attendance Statistics** - Detailed analytics with percentage calculations
- **Visual Reports** - Charts and graphs for attendance trends
- **Low Attendance Alerts** - Automatic identification of students with poor attendance
- **Monthly Trends** - Historical attendance analysis and reporting
- **Export Capabilities** - Generate and download attendance reports

### 🎨 Modern User Interface
- **Responsive Design** - Mobile-first approach with full responsive layout
- **Dark Theme** - Modern dark UI with beautiful gradients and animations
- **Intuitive Navigation** - Clean, user-friendly interface design
- **Real-time Updates** - Live data updates without page refreshes
- **Progressive Web App** - PWA capabilities for mobile installation

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Engine    │
│   (React.js)    │◄──►│   (Django)      │◄──►│   (DeepFace)    │
│                 │    │                 │    │                 │
│ • User Interface│    │ • REST API      │    │ • Face Detection│
│ • Webcam Access │    │ • Authentication│    │ • Recognition   │
│ • Real-time UI  │    │ • Database      │    │ • Model Training│
│ • Responsive    │    │ • File Storage  │    │ • TensorFlow    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** - [Download Python](https://python.org)
- **Node.js 16+** - [Download Node.js](https://nodejs.org)
- **Git** - For cloning the repository
- **Webcam** - For face recognition functionality
- **4GB+ RAM** - For optimal AI model performance

### 🔧 Installation

#### Quick Start Guide

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/facial-attendance-system.git
   cd facial-attendance-system
   ```

2. **Set up the backend** (see detailed steps below)
3. **Set up the frontend** (see detailed steps below)
4. **Access the application** at `http://localhost:3000`

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip and install build tools
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env  # Edit as needed

# Run database migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start Django server
python manage.py runserver 8000
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start React development server
npm start
```

#### Alternative: Docker Setup (Coming Soon)
```bash
# Build and run with Docker Compose
docker-compose up --build
```

> **Note**: Docker configuration files are not included yet but will be added in future releases.

## 🌐 Application URLs

- **Frontend Application**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **Django Admin Panel**: `http://localhost:8000/admin`

## 👤 Default Admin Credentials

```
Email: admin@attendance.com
Password: admin123
```

> ⚠️ **Security Note**: Change these credentials immediately in production!

## 📱 User Guide

### For Students

1. **Registration**
   - Register with your details
   - Capture your face using the webcam
   - Wait for admin approval

2. **Mark Attendance**
   - Login to your dashboard
   - Click \"Mark Attendance\"
   - Look at the camera for face recognition
   - Attendance marked automatically

3. **View Records**
   - Check your attendance history
   - View attendance percentage
   - Monitor your performance

### For Administrators

1. **Dashboard Overview**
   - View system statistics
   - Monitor daily attendance
   - Check low-attendance students

2. **Student Management**
   - Approve new registrations
   - Manage student profiles
   - Handle face re-registration

3. **Reports & Analytics**
   - Generate attendance reports
   - View detailed analytics
   - Export data for external use

## 🛠️ Technical Stack

### Backend Technologies
- **Django 4.2.7** - Web framework
- **Django REST Framework** - API development
- **SQLite/PostgreSQL** - Database
- **DeepFace** - Facial recognition
- **TensorFlow** - Machine learning
- **OpenCV** - Computer vision
- **Pillow** - Image processing

### Frontend Technologies
- **React 18.2.0** - UI framework
- **React Router** - Navigation
- **Axios** - HTTP client
- **React Webcam** - Camera access
- **Chart.js** - Data visualization
- **CSS3** - Modern styling

### AI/ML Components
- **DeepFace Models**: VGG-Face, Facenet, OpenFace, DeepFace
- **Detection Backends**: OpenCV, MTCNN, RetinaFace
- **TensorFlow**: Neural network processing
- **NumPy**: Numerical computations

## 📁 Project Structure

```
Facial_Attendance/
├── 📁 backend/                 # Django backend
│   ├── 📁 apps/
│   │   ├── 📁 authentication/  # User authentication
│   │   ├── 📁 students/        # Student management
│   │   └── 📁 attendance/      # Attendance & face recognition
│   ├── 📁 attendance_system/   # Django project settings
│   ├── 📁 venv/               # Python virtual environment
│   ├── 📄 manage.py           # Django management script
│   ├── 📄 requirements.txt    # Python dependencies
│   ├── 📄 .env               # Environment variables
│   └── 📄 db.sqlite3         # SQLite database
├── 📁 frontend/               # React frontend
│   ├── 📁 src/
│   │   ├── 📁 components/     # Reusable components
│   │   ├── 📁 pages/          # Page components
│   │   ├── 📁 services/       # API services
│   │   ├── 📁 styles/         # CSS styles
│   │   └── 📁 utils/          # Utility functions
│   ├── 📁 public/             # Static assets
│   ├── 📁 node_modules/       # Node.js dependencies
│   └── 📄 package.json       # Node.js dependencies
├── 📄 .gitignore             # Git ignore rules
├── 📄 LICENSE                # MIT License
└── 📄 README.md              # This file
```

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Face Recognition Settings
FACE_RECOGNITION_TOLERANCE=0.6
MAX_FACE_DISTANCE=0.6
DEEPFACE_MODEL=Facenet
DEEPFACE_SIMILARITY_THRESHOLD=0.8
DEEPFACE_DETECTOR_BACKEND=opencv
DEEPFACE_ENFORCE_DETECTION=False

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Face Recognition Models
The system supports multiple AI models:
- **VGG-Face**: High accuracy, slower processing
- **Facenet**: Balanced accuracy and speed (default)
- **OpenFace**: Lightweight, faster processing
- **DeepFace**: Original model, good accuracy

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/register/` - Student registration

### Students
- `GET /api/students/profile/` - Get student profile
- `PUT /api/students/profile/` - Update profile
- `POST /api/students/register-face/` - Register face

### Attendance
- `POST /api/attendance/mark/` - Mark attendance
- `GET /api/attendance/my-records/` - Get attendance records
- `GET /api/attendance/stats/` - Get attendance statistics

### Admin
- `GET /api/admin/analytics/` - System analytics
- `GET /api/admin/students/` - Manage students
- `GET /api/admin/reports/` - Generate reports

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
python manage.py test
```

### Test Face Recognition
```bash
cd backend
python test_deepface_integration.py
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   ```bash
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com
   SECRET_KEY=your-production-secret-key
   ```

2. **Database Migration**
   ```bash
   python manage.py migrate --settings=attendance_system.settings.production
   ```

3. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

4. **Frontend Build**
   ```bash
   npm run build
   ```

### Docker Deployment (Optional)
```dockerfile
# Dockerfile example for backend
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🔍 Troubleshooting

### Common Issues

1. **Face Recognition Not Working**
   - Check camera permissions in browser
   - Verify DeepFace installation: `pip show deepface`
   - Test with: `python backend/test_deepface_integration.py`
   - Ensure good lighting conditions
   - Try different browsers (Chrome recommended)

2. **Installation Errors**
   - Check Python version: `python --version` (3.8+ required)
   - Check Node.js version: `node --version` (16+ required)
   - Clear pip cache: `pip cache purge`
   - Clear npm cache: `npm cache clean --force`
   - On Windows, install Visual Studio Build Tools if needed
   - Ensure all dependencies are properly installed
   - Try installing dependencies one by one to identify problematic packages

3. **Database Issues**
   - Run migrations: `python manage.py migrate`
   - Reset database: Delete `db.sqlite3` and run migrations again
   - Check database permissions
   - Verify Django settings

4. **CORS Errors**
   - Verify CORS settings in `backend/attendance_system/settings.py`
   - Check frontend proxy in `frontend/package.json`
   - Ensure correct URLs in environment variables
   - Clear browser cache

5. **TensorFlow/AI Model Issues**
   - Install Microsoft Visual C++ Redistributable (Windows)
   - Update graphics drivers
   - Try CPU-only TensorFlow if GPU issues persist
   - Increase system RAM if models fail to load

6. **Port Already in Use**
   - Kill processes on ports 3000/8000:
     - Windows: `netstat -ano | findstr :3000` then `taskkill /PID <PID> /F`
     - macOS/Linux: `lsof -ti:3000 | xargs kill -9`
   - Use different ports in configuration

### Performance Optimization

1. **Face Recognition Speed**
   - Use lighter models (OpenFace)
   - Reduce image resolution
   - Optimize detection backends
   - Consider using GPU acceleration if available

2. **Database Performance**
   - Add database indexes
   - Use PostgreSQL for production
   - Implement query optimization
   - Regular database maintenance

3. **System Performance**
   - Ensure adequate RAM (4GB+ recommended)
   - Close unnecessary applications during face recognition
   - Use SSD storage for better I/O performance

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/facial-attendance-system.git
   ```
3. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. **Make your changes**
5. **Test your changes**
   ```bash
   # Backend tests
   cd backend && python manage.py test
   
   # Frontend tests
   cd frontend && npm test
   ```
6. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
7. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write tests for new features
- Update documentation as needed
- Ensure backward compatibility
- Add comments for complex logic
- Update requirements.txt if adding dependencies

### Code Style
- **Python**: Use Black formatter and flake8 linter
- **JavaScript**: Use Prettier formatter and ESLint
- **Commits**: Use conventional commit messages
- **Documentation**: Update README for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DeepFace** - For providing excellent facial recognition capabilities
- **TensorFlow** - For the machine learning framework
- **OpenCV** - For computer vision functionality
- **Django** - For the robust web framework
- **React** - For the modern frontend framework

## 📞 Support

For support and questions:

1. **Check the troubleshooting section** above
2. **Search existing issues** on GitHub
3. **Create a new issue** with detailed information:
   - Operating system and version
   - Python and Node.js versions
   - Error messages and logs
   - Steps to reproduce the issue
4. **Check the documentation** for detailed guides
5. **Join our community** discussions

### Getting Help
- 🐛 **Bug Reports**: Use GitHub Issues
- 💡 **Feature Requests**: Use GitHub Discussions
- ❓ **Questions**: Check FAQ or create a discussion
- 🔒 **Security Issues**: Email maintainers directly

### Response Times
- **Critical bugs**: 24-48 hours
- **General issues**: 3-5 business days
- **Feature requests**: 1-2 weeks
- **Documentation**: 1 week

## 🔮 Future Enhancements

- [ ] **Mobile App** - Native iOS/Android applications
- [ ] **Multi-camera Support** - Multiple camera locations
- [ ] **Advanced Analytics** - ML-powered insights
- [ ] **Integration APIs** - Connect with existing systems
- [ ] **Biometric Backup** - Fingerprint/QR code alternatives
- [ ] **Cloud Deployment** - AWS/Azure deployment guides
- [ ] **Real-time Notifications** - Push notifications for attendance
- [ ] **Bulk Operations** - Mass student management tools

---

<div align=\"center\">
  <p><strong>🎯 Facial Recognition Attendance System</strong></p>
  <p>Making attendance management intelligent and effortless</p>
  <p>⭐ Star this repository if you find it helpful!</p>
</div>
