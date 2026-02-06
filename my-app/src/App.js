import React, { useState } from 'react';
import { authAPI } from './services/api';
import './App.css';

function App() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  
  // Reset flow states
  const [resetStep, setResetStep] = useState(1); // 1: email, 2: code, 3: new password
  const [resetEmail, setResetEmail] = useState('');
  const [resetCode, setResetCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [resetError, setResetError] = useState('');
  const [resetSuccess, setResetSuccess] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 4) {
      newErrors.password = 'Password must be at least 4 characters';
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = validateForm();

    if (Object.keys(newErrors).length === 0) {
      setIsLoading(true);
      setErrors({});
      
      try {
        const response = await authAPI.login(formData.email, formData.password);
        
        // Store the token and user data
        localStorage.setItem('authToken', response.access_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        
        console.log('Login successful:', response);
        alert(`Welcome ${response.user.email}! Role: ${response.user.role}`);
        
        // Redirect to dashboard
        // window.location.href = '/dashboard';
        
      } catch (error) {
        setErrors({
          general: error.message || 'Unable to connect to server. Please try again.'
        });
      } finally {
        setIsLoading(false);
      }
    } else {
      setErrors(newErrors);
    }
  };

  const handleForgotPasswordClick = (e) => {
    e.preventDefault();
    setShowForgotPassword(true);
    setResetStep(1);
    setResetEmail('');
    setResetCode('');
    setNewPassword('');
    setConfirmPassword('');
    setResetError('');
    setResetSuccess(false);
  };

  const handleCloseForgotPassword = () => {
    setShowForgotPassword(false);
  };

  // Step 1: Send reset code to email
  const handleSendResetCode = async (e) => {
    e.preventDefault();
    
    if (!resetEmail || !/\S+@\S+\.\S+/.test(resetEmail)) {
      setResetError('Please enter a valid email');
      return;
    }

    setIsLoading(true);
    setResetError('');
    
    try {
      await authAPI.forgotPassword(resetEmail);
      setResetStep(2); // Move to code verification step
    } catch (error) {
      setResetError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Step 2: Verify code
  const handleVerifyCode = async (e) => {
    e.preventDefault();
    
    if (!resetCode || resetCode.length !== 6) {
      setResetError('Please enter the 6-digit code');
      return;
    }

    setIsLoading(true);
    setResetError('');
    
    try {
      await authAPI.verifyResetCode(resetEmail, resetCode);
      setResetStep(3); // Move to new password step
    } catch (error) {
      setResetError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Step 3: Set new password
  const handleSetNewPassword = async (e) => {
    e.preventDefault();
    
    if (!newPassword || newPassword.length < 4) {
      setResetError('Password must be at least 4 characters');
      return;
    }
    
    if (newPassword !== confirmPassword) {
      setResetError('Passwords do not match');
      return;
    }

    setIsLoading(true);
    setResetError('');
    
    try {
      await authAPI.resetPassword(resetEmail, resetCode, newPassword);
      setResetSuccess(true);
    } catch (error) {
      setResetError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1 className="login-title">Admin Portal</h1>
          <p className="login-subtitle">
            Sign in to access the administration panel
          </p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {errors.general && (
            <div className="error-banner">{errors.general}</div>
          )}

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className={`form-input ${errors.email ? 'input-error' : ''}`}
              placeholder="admin@example.com"
            />
            {errors.email && <span className="error-message">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className={`form-input ${errors.password ? 'input-error' : ''}`}
              placeholder="Enter your password"
            />
            {errors.password && <span className="error-message">{errors.password}</span>}
          </div>

          <div className="form-options">
            <label className="remember-me">
              <input type="checkbox" className="checkbox" />
              <span>Remember me</span>
            </label>
            <button type="button" className="forgot-password-btn" onClick={handleForgotPasswordClick}>
              Forgot password?
            </button>
          </div>

          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>
      </div>

      {/* Forgot Password Modal */}
      {showForgotPassword && (
        <div className="modal-overlay" onClick={handleCloseForgotPassword}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={handleCloseForgotPassword}>
              ×
            </button>
            
            {!resetSuccess ? (
              <>
                <h2 className="modal-title">
                  {resetStep === 1 && "Reset Password"}
                  {resetStep === 2 && "Enter Verification Code"}
                  {resetStep === 3 && "Set New Password"}
                </h2>
                
                <p className="modal-description">
                  {resetStep === 1 && "Enter your email to receive a verification code."}
                  {resetStep === 2 && `Enter the 6-digit code sent to ${resetEmail}`}
                  {resetStep === 3 && "Create a new password for your account."}
                </p>
                
                {resetError && (
                  <div className="error-banner">{resetError}</div>
                )}
                
                {/* Step 1: Email Form */}
                {resetStep === 1 && (
                  <form onSubmit={handleSendResetCode} className="modal-form">
                    <div className="form-group">
                      <label className="form-label">Email Address</label>
                      <input
                        type="email"
                        value={resetEmail}
                        onChange={(e) => setResetEmail(e.target.value)}
                        className="form-input"
                        placeholder="Enter your email"
                        autoFocus
                      />
                    </div>
                    
                    <div className="modal-buttons">
                      <button type="button" className="btn-secondary" onClick={handleCloseForgotPassword}>
                        Cancel
                      </button>
                      <button type="submit" className="btn-primary" disabled={isLoading}>
                        {isLoading ? 'Sending...' : 'Send Code'}
                      </button>
                    </div>
                  </form>
                )}
                
                {/* Step 2: Code Verification */}
                {resetStep === 2 && (
                  <form onSubmit={handleVerifyCode} className="modal-form">
                    <div className="form-group">
                      <label className="form-label">Verification Code</label>
                      <input
                        type="text"
                        value={resetCode}
                        onChange={(e) => setResetCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                        className="form-input code-input"
                        placeholder="000000"
                        maxLength="6"
                        autoFocus
                      />
                      <p className="form-hint">Enter the 6-digit code from your email</p>
                    </div>
                    
                    <div className="modal-buttons">
                      <button type="button" className="btn-secondary" onClick={() => setResetStep(1)}>
                        Back
                      </button>
                      <button type="submit" className="btn-primary" disabled={isLoading}>
                        {isLoading ? 'Verifying...' : 'Verify Code'}
                      </button>
                    </div>
                  </form>
                )}
                
                {/* Step 3: New Password */}
                {resetStep === 3 && (
                  <form onSubmit={handleSetNewPassword} className="modal-form">
                    <div className="form-group">
                      <label className="form-label">New Password</label>
                      <input
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="form-input"
                        placeholder="Enter new password"
                        autoFocus
                      />
                    </div>
                    
                    <div className="form-group">
                      <label className="form-label">Confirm Password</label>
                      <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="form-input"
                        placeholder="Confirm new password"
                      />
                    </div>
                    
                    <div className="modal-buttons">
                      <button type="button" className="btn-secondary" onClick={() => setResetStep(2)}>
                        Back
                      </button>
                      <button type="submit" className="btn-primary" disabled={isLoading}>
                        {isLoading ? 'Resetting...' : 'Reset Password'}
                      </button>
                    </div>
                  </form>
                )}
              </>
            ) : (
              <div className="success-container">
                <div className="success-icon">✓</div>
                <h2 className="modal-title">Password Reset Complete!</h2>
                <p className="modal-description">
                  Your password has been successfully reset.
                </p>
                <p className="modal-description-small">
                  You can now sign in with your new password.
                </p>
                <button 
                  className="btn-primary btn-full-width" 
                  onClick={handleCloseForgotPassword}
                >
                  Back to Login
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;