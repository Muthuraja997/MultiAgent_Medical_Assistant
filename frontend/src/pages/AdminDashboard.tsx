import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  Stethoscope, 
  Calendar, 
  TrendingUp, 
  UserPlus, 
  RefreshCw,
  Edit,
  Trash2,
  Check,
  X,
  Clock
} from 'lucide-react';

interface User {
  _id: string;
  user_id: string;
  user_name: string;
  user_type: 'PATIENT' | 'DOCTOR' | 'ADMIN';
  doctor_id?: string;
}

interface Doctor {
  _id: string;
  doctor_id: string;
  doc_name: string;
  available_status: boolean;
  meet_link?: string;
  start_meet_time?: string;
  end_meet_time?: string;
}

interface Appointment {
  _id: string;
  user_id: string;
  doctor_id: string;
  appointment_status: 'SCHEDULED' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
  scheduled_time: string;
  meet_link?: string;
}

interface Statistics {
  total_users: number;
  total_doctors: number;
  total_appointments: number;
  active_appointments: number;
  available_doctors: number;
}

const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'users' | 'doctors' | 'appointments'>('users');
  const [users, setUsers] = useState<User[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [statistics, setStatistics] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [showUserForm, setShowUserForm] = useState(false);
  const [showDoctorForm, setShowDoctorForm] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [editingDoctor, setEditingDoctor] = useState<Doctor | null>(null);

  // Form data
  const [userForm, setUserForm] = useState({
    user_id: '',
    user_name: '',
    user_type: 'PATIENT' as 'PATIENT' | 'DOCTOR' | 'ADMIN',
    doctor_id: ''
  });

  const [doctorForm, setDoctorForm] = useState({
    doctor_id: '',
    doc_name: '',
    available_status: true,
    meet_link: '',
    start_meet_time: '',
    end_meet_time: ''
  });

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, usersRes, doctorsRes, appointmentsRes] = await Promise.all([
        fetch('/api/admin/statistics'),
        fetch('/api/users'),
        fetch('/api/doctors'),
        fetch('/api/appointments')
      ]);

      if (statsRes.ok) setStatistics(await statsRes.json());
      if (usersRes.ok) setUsers(await usersRes.json());
      if (doctorsRes.ok) setDoctors(await doctorsRes.json());
      if (appointmentsRes.ok) setAppointments(await appointmentsRes.json());
    } catch (err) {
      setError('Failed to fetch data');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userForm)
      });
      
      if (response.ok) {
        setShowUserForm(false);
        resetUserForm();
        fetchData();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to create user');
      }
    } catch (err) {
      alert('Failed to create user');
    }
  };

  const handleUpdateUser = async (userId: string) => {
    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userForm)
      });
      
      if (response.ok) {
        setEditingUser(null);
        resetUserForm();
        fetchData();
      }
    } catch (err) {
      alert('Failed to update user');
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user?')) return;
    
    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        fetchData();
      }
    } catch (err) {
      alert('Failed to delete user');
    }
  };

  const handleCreateDoctor = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/doctors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(doctorForm)
      });
      
      if (response.ok) {
        setShowDoctorForm(false);
        resetDoctorForm();
        fetchData();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to create doctor');
      }
    } catch (err) {
      alert('Failed to create doctor');
    }
  };

  const handleUpdateDoctor = async (doctorId: string) => {
    try {
      const response = await fetch(`/api/doctors/${doctorId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(doctorForm)
      });
      
      if (response.ok) {
        setEditingDoctor(null);
        resetDoctorForm();
        fetchData();
      }
    } catch (err) {
      alert('Failed to update doctor');
    }
  };

  const handleDeleteDoctor = async (doctorId: string) => {
    if (!confirm('Are you sure you want to delete this doctor?')) return;
    
    try {
      const response = await fetch(`/api/doctors/${doctorId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        fetchData();
      }
    } catch (err) {
      alert('Failed to delete doctor');
    }
  };

  const toggleDoctorAvailability = async (doctorId: string, available: boolean) => {
    try {
      const response = await fetch(`/api/doctors/${doctorId}/availability?available=${available}`, {
        method: 'PATCH'
      });
      
      if (response.ok) {
        fetchData();
      }
    } catch (err) {
      alert('Failed to update availability');
    }
  };

  const resetUserForm = () => {
    setUserForm({
      user_id: '',
      user_name: '',
      user_type: 'PATIENT',
      doctor_id: ''
    });
  };

  const resetDoctorForm = () => {
    setDoctorForm({
      doctor_id: '',
      doc_name: '',
      available_status: true,
      meet_link: '',
      start_meet_time: '',
      end_meet_time: ''
    });
  };

  const editUser = (user: User) => {
    setEditingUser(user);
    setUserForm({
      user_id: user.user_id,
      user_name: user.user_name,
      user_type: user.user_type,
      doctor_id: user.doctor_id || ''
    });
    setShowUserForm(true);
  };

  const editDoctor = (doctor: Doctor) => {
    setEditingDoctor(doctor);
    setDoctorForm({
      doctor_id: doctor.doctor_id,
      doc_name: doctor.doc_name,
      available_status: doctor.available_status,
      meet_link: doctor.meet_link || '',
      start_meet_time: doctor.start_meet_time || '',
      end_meet_time: doctor.end_meet_time || ''
    });
    setShowDoctorForm(true);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'SCHEDULED': return 'text-blue-600 bg-blue-100';
      case 'ACTIVE': return 'text-green-600 bg-green-100';
      case 'COMPLETED': return 'text-gray-600 bg-gray-100';
      case 'CANCELLED': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Admin Dashboard</h1>
          <p className="text-gray-600">Manage users, doctors, and appointments</p>
        </div>

        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-xl p-6 shadow-lg border border-blue-100"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Total Users</p>
                  <p className="text-3xl font-bold text-blue-600">{statistics.total_users}</p>
                </div>
                <Users className="w-12 h-12 text-blue-400" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white rounded-xl p-6 shadow-lg border border-purple-100"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Total Doctors</p>
                  <p className="text-3xl font-bold text-purple-600">{statistics.total_doctors}</p>
                </div>
                <Stethoscope className="w-12 h-12 text-purple-400" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-xl p-6 shadow-lg border border-green-100"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Available Doctors</p>
                  <p className="text-3xl font-bold text-green-600">{statistics.available_doctors}</p>
                </div>
                <TrendingUp className="w-12 h-12 text-green-400" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-xl p-6 shadow-lg border border-orange-100"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Appointments</p>
                  <p className="text-3xl font-bold text-orange-600">{statistics.total_appointments}</p>
                </div>
                <Calendar className="w-12 h-12 text-orange-400" />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white rounded-xl p-6 shadow-lg border border-red-100"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Active Now</p>
                  <p className="text-3xl font-bold text-red-600">{statistics.active_appointments}</p>
                </div>
                <Clock className="w-12 h-12 text-red-400" />
              </div>
            </motion.div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex space-x-4 mb-6">
          <button
            onClick={() => setActiveTab('users')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'users'
                ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Users className="w-5 h-5 inline mr-2" />
            Users
          </button>
          <button
            onClick={() => setActiveTab('doctors')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'doctors'
                ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Stethoscope className="w-5 h-5 inline mr-2" />
            Doctors
          </button>
          <button
            onClick={() => setActiveTab('appointments')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === 'appointments'
                ? 'bg-gradient-to-r from-green-600 to-green-700 text-white shadow-lg'
                : 'bg-white text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Calendar className="w-5 h-5 inline mr-2" />
            Appointments
          </button>
          <button
            onClick={fetchData}
            className="ml-auto px-6 py-3 rounded-lg font-semibold bg-white text-gray-600 hover:bg-gray-50 transition-all"
          >
            <RefreshCw className={`w-5 h-5 inline mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Users Tab */}
        {activeTab === 'users' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white rounded-xl shadow-lg p-6"
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">User Management</h2>
              <button
                onClick={() => {
                  resetUserForm();
                  setEditingUser(null);
                  setShowUserForm(!showUserForm);
                }}
                className="px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:shadow-lg transition-all"
              >
                <UserPlus className="w-5 h-5 inline mr-2" />
                Add User
              </button>
            </div>

            {/* User Form */}
            {showUserForm && (
              <motion.form
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                onSubmit={editingUser ? (e) => { e.preventDefault(); handleUpdateUser(editingUser.user_id); } : handleCreateUser}
                className="mb-6 p-6 bg-gray-50 rounded-lg border border-gray-200"
              >
                <h3 className="text-lg font-semibold mb-4">{editingUser ? 'Edit User' : 'Create New User'}</h3>
                <div className="grid grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="User ID"
                    value={userForm.user_id}
                    onChange={(e) => setUserForm({ ...userForm, user_id: e.target.value })}
                    className="px-4 py-2 border rounded-lg"
                    required
                    disabled={!!editingUser}
                  />
                  <input
                    type="text"
                    placeholder="User Name"
                    value={userForm.user_name}
                    onChange={(e) => setUserForm({ ...userForm, user_name: e.target.value })}
                    className="px-4 py-2 border rounded-lg"
                    required
                  />
                  <select
                    value={userForm.user_type}
                    onChange={(e) => setUserForm({ ...userForm, user_type: e.target.value as any })}
                    className="px-4 py-2 border rounded-lg"
                  >
                    <option value="PATIENT">Patient</option>
                    <option value="DOCTOR">Doctor</option>
                    <option value="ADMIN">Admin</option>
                  </select>
                  <input
                    type="text"
                    placeholder="Doctor ID (optional)"
                    value={userForm.doctor_id}
                    onChange={(e) => setUserForm({ ...userForm, doctor_id: e.target.value })}
                    className="px-4 py-2 border rounded-lg"
                  />
                </div>
                <div className="flex space-x-2 mt-4">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    {editingUser ? 'Update' : 'Create'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowUserForm(false);
                      setEditingUser(null);
                      resetUserForm();
                    }}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </motion.form>
            )}

            {/* Users Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">User ID</th>
                    <th className="text-left py-3 px-4">Name</th>
                    <th className="text-left py-3 px-4">Type</th>
                    <th className="text-left py-3 px-4">Doctor ID</th>
                    <th className="text-right py-3 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user._id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-mono text-sm">{user.user_id}</td>
                      <td className="py-3 px-4">{user.user_name}</td>
                      <td className="py-3 px-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          user.user_type === 'ADMIN' ? 'bg-red-100 text-red-600' :
                          user.user_type === 'DOCTOR' ? 'bg-purple-100 text-purple-600' :
                          'bg-blue-100 text-blue-600'
                        }`}>
                          {user.user_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-sm">{user.doctor_id || '-'}</td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => editUser(user)}
                          className="text-blue-600 hover:text-blue-800 mr-3"
                        >
                          <Edit className="w-4 h-4 inline" />
                        </button>
                        <button
                          onClick={() => handleDeleteUser(user.user_id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4 inline" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {/* Doctors Tab */}
        {activeTab === 'doctors' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white rounded-xl shadow-lg p-6"
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Doctor Management</h2>
              <button
                onClick={() => {
                  resetDoctorForm();
                  setEditingDoctor(null);
                  setShowDoctorForm(!showDoctorForm);
                }}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:shadow-lg transition-all"
              >
                <UserPlus className="w-5 h-5 inline mr-2" />
                Add Doctor
              </button>
            </div>

            {/* Doctor Form */}
            {showDoctorForm && (
              <motion.form
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                onSubmit={editingDoctor ? (e) => { e.preventDefault(); handleUpdateDoctor(editingDoctor.doctor_id); } : handleCreateDoctor}
                className="mb-6 p-6 bg-gray-50 rounded-lg border border-gray-200"
              >
                <h3 className="text-lg font-semibold mb-4">{editingDoctor ? 'Edit Doctor' : 'Create New Doctor'}</h3>
                <div className="grid grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Doctor ID"
                    value={doctorForm.doctor_id}
                    onChange={(e) => setDoctorForm({ ...doctorForm, doctor_id: e.target.value })}
                    className="px-4 py-2 border rounded-lg"
                    required
                    disabled={!!editingDoctor}
                  />
                  <input
                    type="text"
                    placeholder="Doctor Name"
                    value={doctorForm.doc_name}
                    onChange={(e) => setDoctorForm({ ...doctorForm, doc_name: e.target.value })}
                    className="px-4 py-2 border rounded-lg"
                    required
                  />
                  <input
                    type="text"
                    placeholder="Meet Link"
                    value={doctorForm.meet_link}
                    onChange={(e) => setDoctorForm({ ...doctorForm, meet_link: e.target.value })}
                    className="px-4 py-2 border rounded-lg"
                  />
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      checked={doctorForm.available_status}
                      onChange={(e) => setDoctorForm({ ...doctorForm, available_status: e.target.checked })}
                      className="mr-2"
                    />
                    <label>Available</label>
                  </div>
                  <input
                    type="time"
                    placeholder="Start Time"
                    value={doctorForm.start_meet_time}
                    onChange={(e) => setDoctorForm({ ...doctorForm, start_meet_time: e.target.value })}
                    className="px-4 py-2 border rounded-lg"
                  />
                  <input
                    type="time"
                    placeholder="End Time"
                    value={doctorForm.end_meet_time}
                    onChange={(e) => setDoctorForm({ ...doctorForm, end_meet_time: e.target.value })}
                    className="px-4 py-2 border rounded-lg"
                  />
                </div>
                <div className="flex space-x-2 mt-4">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                  >
                    {editingDoctor ? 'Update' : 'Create'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowDoctorForm(false);
                      setEditingDoctor(null);
                      resetDoctorForm();
                    }}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </motion.form>
            )}

            {/* Doctors Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">Doctor ID</th>
                    <th className="text-left py-3 px-4">Name</th>
                    <th className="text-left py-3 px-4">Availability</th>
                    <th className="text-left py-3 px-4">Schedule</th>
                    <th className="text-left py-3 px-4">Meet Link</th>
                    <th className="text-right py-3 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {doctors.map((doctor) => (
                    <tr key={doctor._id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-mono text-sm">{doctor.doctor_id}</td>
                      <td className="py-3 px-4">{doctor.doc_name}</td>
                      <td className="py-3 px-4">
                        <button
                          onClick={() => toggleDoctorAvailability(doctor.doctor_id, !doctor.available_status)}
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            doctor.available_status
                              ? 'bg-green-100 text-green-600'
                              : 'bg-red-100 text-red-600'
                          }`}
                        >
                          {doctor.available_status ? (
                            <><Check className="w-3 h-3 inline mr-1" />Available</>
                          ) : (
                            <><X className="w-3 h-3 inline mr-1" />Unavailable</>
                          )}
                        </button>
                      </td>
                      <td className="py-3 px-4 text-sm">
                        {doctor.start_meet_time && doctor.end_meet_time
                          ? `${doctor.start_meet_time} - ${doctor.end_meet_time}`
                          : '-'}
                      </td>
                      <td className="py-3 px-4 text-sm truncate max-w-xs">
                        {doctor.meet_link || '-'}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => editDoctor(doctor)}
                          className="text-blue-600 hover:text-blue-800 mr-3"
                        >
                          <Edit className="w-4 h-4 inline" />
                        </button>
                        <button
                          onClick={() => handleDeleteDoctor(doctor.doctor_id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 className="w-4 h-4 inline" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {/* Appointments Tab */}
        {activeTab === 'appointments' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white rounded-xl shadow-lg p-6"
          >
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Appointment Management</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">User ID</th>
                    <th className="text-left py-3 px-4">Doctor ID</th>
                    <th className="text-left py-3 px-4">Status</th>
                    <th className="text-left py-3 px-4">Scheduled Time</th>
                    <th className="text-left py-3 px-4">Meet Link</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.map((apt) => (
                    <tr key={apt._id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4 font-mono text-sm">{apt.user_id}</td>
                      <td className="py-3 px-4 font-mono text-sm">{apt.doctor_id}</td>
                      <td className="py-3 px-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(apt.appointment_status)}`}>
                          {apt.appointment_status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm">
                        {new Date(apt.scheduled_time).toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-sm truncate max-w-xs">
                        {apt.meet_link || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;
