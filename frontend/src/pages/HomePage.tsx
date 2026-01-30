import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { UserCog, CheckCircle, XCircle, Calendar, Clock, Send, Loader } from 'lucide-react';

interface Doctor {
  doctor_id: string;
  doc_name: string;
  available_status: boolean;
  email?: string;
  phone?: string;
}

interface AppointmentRequest {
  doctor_id: string;
  reason: string;
  preferred_date: string;
  preferred_time: string;
}

const HomePage: React.FC = () => {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedDoctor, setSelectedDoctor] = useState<Doctor | null>(null);
  const [formData, setFormData] = useState<AppointmentRequest>({
    doctor_id: '',
    reason: '',
    preferred_date: '',
    preferred_time: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const userId = localStorage.getItem('user_id');
  const userType = localStorage.getItem('user_type');

  useEffect(() => {
    fetchDoctors();
  }, []);

  const fetchDoctors = async () => {
    try {
      const response = await fetch('/api/doctors');
      const data = await response.json();
      
      // Filter only available doctors
      const availableDoctors = data.filter((doc: Doctor) => doc.available_status === true);
      setDoctors(availableDoctors);
    } catch (error) {
      console.error('Error fetching doctors:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestAppointment = (doctor: Doctor) => {
    setSelectedDoctor(doctor);
    setFormData({
      ...formData,
      doctor_id: doctor.doctor_id
    });
    setShowModal(true);
    setMessage({ type: '', text: '' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch('/api/appointment-requests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          user_id: userId // Include user_id in the request
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({
          type: 'success',
          text: 'Appointment request sent successfully! The doctor will review your request.'
        });
        setTimeout(() => {
          setShowModal(false);
          setFormData({
            doctor_id: '',
            reason: '',
            preferred_date: '',
            preferred_time: ''
          });
        }, 2000);
      } else {
        setMessage({
          type: 'error',
          text: data.detail || 'Failed to send appointment request'
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Connection error. Please try again.'
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  // Hide for doctors - they don't need to see this page
  if (userType === 'DOCTOR') {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Doctor Dashboard</h2>
        <p className="text-gray-600">Welcome! Check the Video Consultation page to manage your appointment requests.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Available Doctors</h1>
        <p className="text-gray-600">
          Browse our available doctors and request an appointment
        </p>
      </div>

      {/* Doctors Grid */}
      {doctors.length === 0 ? (
        <div className="bg-white rounded-xl shadow-lg p-12 text-center">
          <XCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700 mb-2">No Doctors Available</h2>
          <p className="text-gray-500">All doctors are currently busy. Please check back later.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {doctors.map((doctor) => (
            <motion.div
              key={doctor.doctor_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              whileHover={{ y: -5 }}
              className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100"
            >
              <div className="p-6">
                {/* Doctor Icon */}
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
                  <UserCog className="w-8 h-8 text-white" />
                </div>

                {/* Doctor Info */}
                <h3 className="text-xl font-bold text-gray-800 mb-2">{doctor.doc_name}</h3>
                <p className="text-sm text-gray-600 mb-1">ID: {doctor.doctor_id}</p>
                
                {doctor.email && (
                  <p className="text-sm text-gray-600 mb-1">📧 {doctor.email}</p>
                )}
                {doctor.phone && (
                  <p className="text-sm text-gray-600 mb-3">📱 {doctor.phone}</p>
                )}

                {/* Status Badge */}
                <div className="flex items-center mb-4">
                  <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                  <span className="text-sm font-semibold text-green-600">Available</span>
                </div>

                {/* Request Button */}
                <button
                  onClick={() => handleRequestAppointment(doctor)}
                  className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all"
                >
                  Request Appointment
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Appointment Request Modal */}
      {showModal && selectedDoctor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6"
          >
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Request Appointment
            </h2>
            <p className="text-gray-600 mb-6">
              Dr. {selectedDoctor.doc_name}
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Reason */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reason for Appointment
                </label>
                <textarea
                  value={formData.reason}
                  onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Describe your symptoms or reason for consultation..."
                  rows={3}
                  required
                />
              </div>

              {/* Preferred Date */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Date
                </label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="date"
                    value={formData.preferred_date}
                    onChange={(e) => setFormData({ ...formData, preferred_date: e.target.value })}
                    min={new Date().toISOString().split('T')[0]}
                    className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
              </div>

              {/* Preferred Time */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Time
                </label>
                <div className="relative">
                  <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="time"
                    value={formData.preferred_time}
                    onChange={(e) => setFormData({ ...formData, preferred_time: e.target.value })}
                    className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>
              </div>

              {/* Message */}
              {message.text && (
                <div
                  className={`p-3 rounded-lg ${
                    message.type === 'success'
                      ? 'bg-green-50 text-green-700 border border-green-200'
                      : 'bg-red-50 text-red-700 border border-red-200'
                  }`}
                >
                  {message.text}
                </div>
              )}

              {/* Buttons */}
              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 py-3 border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-all"
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {submitting ? (
                    <>
                      <Loader className="w-5 h-5 animate-spin mr-2" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5 mr-2" />
                      Send Request
                    </>
                  )}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default HomePage;
