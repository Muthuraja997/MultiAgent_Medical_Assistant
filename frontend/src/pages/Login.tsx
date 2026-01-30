import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LogIn, User, Lock, UserCog, Activity } from 'lucide-react';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    user_id: '',
    password: '',
    user_type: 'USER' as 'USER' | 'DOCTOR'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (data.success) {
        // Store user info in localStorage
        localStorage.setItem('user_id', data.user_id);
        localStorage.setItem('user_name', data.user_name);
        localStorage.setItem('user_type', data.user_type);
        localStorage.setItem('token', data.token || '');

        // Navigate to dashboard
        navigate('/dashboard');
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err) {
      setError('Connection error. Please try again.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-pink-500 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 260, damping: 20 }}
            className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-2xl"
          >
            <Activity className="w-12 h-12 text-blue-600" />
          </motion.div>
          <h1 className="text-4xl font-bold text-white mb-2">Medical AI Assistant</h1>
          <p className="text-blue-100">Intelligent Healthcare Platform</p>
        </div>

        {/* Login Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-2xl p-8"
        >
          <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Welcome Back</h2>

          {/* User Type Toggle */}
          <div className="flex space-x-4 mb-6">
            <button
              type="button"
              onClick={() => setFormData({ ...formData, user_type: 'USER' })}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all ${
                formData.user_type === 'USER'
                  ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <User className="w-5 h-5 inline mr-2" />
              User
            </button>
            <button
              type="button"
              onClick={() => setFormData({ ...formData, user_type: 'DOCTOR' })}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all ${
                formData.user_type === 'DOCTOR'
                  ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <UserCog className="w-5 h-5 inline mr-2" />
              Doctor
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* User ID Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {formData.user_type === 'USER' ? 'User ID' : 'Doctor ID'}
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={formData.user_id}
                  onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
                  className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder={`Enter your ${formData.user_type === 'USER' ? 'user' : 'doctor'} ID`}
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="Enter your password"
                  required
                />
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm"
              >
                {error}
              </motion.div>
            )}

            {/* Login Button */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 rounded-lg font-semibold text-white transition-all ${
                loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : formData.user_type === 'USER'
                  ? 'bg-gradient-to-r from-blue-600 to-blue-700 hover:shadow-lg'
                  : 'bg-gradient-to-r from-purple-600 to-purple-700 hover:shadow-lg'
              }`}
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Logging in...
                </span>
              ) : (
                <span className="flex items-center justify-center">
                  <LogIn className="w-5 h-5 mr-2" />
                  Login
                </span>
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 mb-3">
              Demo Users:
              <span className="text-xs text-gray-500 block mt-1">
                User: user_001 | Doctor: doc_001
              </span>
            </p>
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link 
                to="/register" 
                className={`font-semibold ${
                  formData.user_type === 'USER' 
                    ? 'text-blue-600 hover:text-blue-700' 
                    : 'text-purple-600 hover:text-purple-700'
                }`}
              >
                Create one here
              </Link>
            </p>
          </div>
        </motion.div>

        {/* Footer Text */}
        <p className="text-center text-white text-sm mt-6 opacity-80">
          © 2024 Medical AI Assistant. All rights reserved.
        </p>
      </motion.div>
    </div>
  );
};

export default Login;
