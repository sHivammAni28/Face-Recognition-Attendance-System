import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './utils/AuthContext';
import Navbar from './components/Navbar';
import Login from './pages/Login';
import StudentRegistration from './pages/StudentRegistration';
import StudentDashboard from './pages/StudentDashboard';
import AdminDashboard from './pages/AdminDashboard';
import MarkAttendance from './pages/MarkAttendance';
import ViewAttendance from './pages/ViewAttendance';
import FaceRegistration from './pages/FaceRegistration';
import StudentManagement from './pages/StudentManagement';
import AttendanceReports from './pages/AttendanceReports';
import NotFound from './pages/NotFound';
import './styles/App.css';

// Protected Route Component
const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="loading">Loading...</div>;
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }
  
  return children;
};

// Public Route Component (redirect if already logged in)
const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="loading">Loading...</div>;
  }
  
  if (user) {
    const redirectPath = user.role === 'admin' ? '/admin' : '/student';
    return <Navigate to={redirectPath} replace />;
  }
  
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppContent />
        </div>
      </Router>
    </AuthProvider>
  );
}

// Separate component to access useAuth hook
const AppContent = () => {
  const { user } = useAuth();
  
  return (
    <>
      <Navbar />
      <main className={`main-content ${user ? 'with-navbar' : 'no-navbar'}`}>
        <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Navigate to="/login" replace />} />
              <Route path="/login" element={
                <PublicRoute>
                  <Login />
                </PublicRoute>
              } />
              <Route path="/register" element={
                <PublicRoute>
                  <StudentRegistration />
                </PublicRoute>
              } />
              
              {/* Student Routes */}
              <Route path="/student" element={
                <ProtectedRoute requiredRole="student">
                  <StudentDashboard />
                </ProtectedRoute>
              } />
              <Route path="/student/mark-attendance" element={
                <ProtectedRoute requiredRole="student">
                  <MarkAttendance />
                </ProtectedRoute>
              } />
              <Route path="/student/view-attendance" element={
                <ProtectedRoute requiredRole="student">
                  <ViewAttendance />
                </ProtectedRoute>
              } />
              <Route path="/student/register-face" element={
                <ProtectedRoute requiredRole="student">
                  <FaceRegistration />
                </ProtectedRoute>
              } />
              
              {/* Admin Routes */}
              <Route path="/admin" element={
                <ProtectedRoute requiredRole="admin">
                  <AdminDashboard />
                </ProtectedRoute>
              } />
              <Route path="/admin/students" element={
                <ProtectedRoute requiredRole="admin">
                  <StudentManagement />
                </ProtectedRoute>
              } />
              <Route path="/admin/reports" element={
                <ProtectedRoute requiredRole="admin">
                  <AttendanceReports />
                </ProtectedRoute>
              } />
              
              {/* Error Routes */}
              <Route path="/unauthorized" element={
                <div className="error-page">
                  <h2>Unauthorized Access</h2>
                  <p>You don't have permission to access this page.</p>
                </div>
              } />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
        </>
  );
};

export default App;