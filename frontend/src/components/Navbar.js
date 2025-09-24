import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import '../styles/Navbar.css';

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    setMobileMenuOpen(false);
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const isActive = (path) => {
    return location.pathname === path ? 'nav-link active' : 'nav-link';
  };

  if (!user) {
    return null; // Don't show navbar on login/register pages
  }

  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/" className="navbar-brand">
          📚 Attendance System
        </Link>

        <button 
          className="mobile-menu-toggle"
          onClick={toggleMobileMenu}
        >
          ☰
        </button>

        <ul className={`navbar-nav ${mobileMenuOpen ? 'mobile-open' : ''}`}>
          {user.role === 'student' && (
            <>
              <li>
                <Link 
                  to="/student" 
                  className={isActive('/student')}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>
              </li>
              <li>
                <Link 
                  to="/student/mark-attendance" 
                  className={isActive('/student/mark-attendance')}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Mark Attendance
                </Link>
              </li>
              <li>
                <Link 
                  to="/student/view-attendance" 
                  className={isActive('/student/view-attendance')}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  View Attendance
                </Link>
              </li>
            </>
          )}

          {user.role === 'admin' && (
            <>
              <li>
                <Link 
                  to="/admin" 
                  className={isActive('/admin')}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>
              </li>
              <li>
                <Link 
                  to="/admin/students" 
                  className={isActive('/admin/students')}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Students
                </Link>
              </li>
              <li>
                <Link 
                  to="/admin/reports" 
                  className={isActive('/admin/reports')}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Reports
                </Link>
              </li>
            </>
          )}

          <li className="user-info">
            {/* <span className="welcome-text">
              Welcome, {user.first_name || user.username}!
            </span> */}
            <button 
              onClick={handleLogout} 
              className="logout-btn"
            >
              Logout
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;