import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Video,
  Calendar,
  Clock,
  User,
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader,
  RefreshCw,
  Trash2,
} from 'lucide-react';
import { api } from '../services/api';

interface AppointmentRequest {
  request_id: string;
  user_id: string;
  user_name: string;
  doctor_id: string;
  doctor_name: string;
  reason: string;
  preferred_date: string;
  preferred_time: string;
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED';
  meet_link?: string;
  meeting_id?: string;
  created_at: string;
}

const VideoConsultation = () => {
  const [appointmentRequests, setAppointmentRequests] = useState<AppointmentRequest[]>([]);
  const [userRequests, setUserRequests] = useState<AppointmentRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<string | null>(null);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [refreshing, setRefreshing] = useState(false);

  const userId = localStorage.getItem('user_id');
  const userType = localStorage.getItem('user_type');

  useEffect(() => {
    fetchAppointmentRequests();
    const interval = setInterval(() => {
      fetchAppointmentRequests(true);
    }, 10000);
    return () => clearInterval(interval);
  }, [userId, userType]);

  const fetchAppointmentRequests = async (silent = false) => {
    if (!silent) {
      setLoading(true);
    } else {
      setRefreshing(true);
    }

    try {
      if (userType === 'DOCTOR') {
        const response = await fetch(`/api/appointment-requests/doctor/${userId}`);
        const data = await response.json();
        setAppointmentRequests(data);
      } else if (userType === 'USER') {
        const response = await fetch(`/api/appointment-requests/user/${userId}`);
        const data = await response.json();
        setUserRequests(data);
      }
    } catch (error) {
      console.error('Error fetching appointment requests:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleAccept = (request: AppointmentRequest) => {
    if (!window.confirm(`Accept appointment request from ${request.user_name}?\n\nA Jitsi meeting link will be automatically created.`)) {
      return;
    }
    
    confirmAccept(request);
  };

  const confirmAccept = async (request: AppointmentRequest) => {
    setProcessing(request.request_id);
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch(`/api/appointment-requests/${request.request_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: 'ACCEPTED',
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessage({ 
          type: 'success', 
          text: `Appointment accepted! Meeting link: ${data.meet_link || 'Generated'}` 
        });
        setTimeout(() => {
          fetchAppointmentRequests();
          setMessage({ type: '', text: '' });
        }, 3000);
      } else {
        const data = await response.json();
        setMessage({ type: 'error', text: data.detail || 'Failed to accept appointment' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Connection error. Please try again.' });
    } finally {
      setProcessing(null);
    }
  };

  const handleConsultationComplete = async (request: AppointmentRequest) => {
    if (
      !window.confirm(
        'Mark this consultation as finished? The appointment and meeting link will be removed from your lists.'
      )
    ) {
      return;
    }
    if (!userId) return;
    setProcessing(request.request_id);
    setMessage({ type: '', text: '' });
    try {
      await api.completeAppointmentConsultation(request.request_id, userId);
      setMessage({ type: 'success', text: 'Consultation ended. Appointment removed.' });
      await fetchAppointmentRequests(true);
    } catch (err: unknown) {
      const ax = err as { response?: { data?: { detail?: string } } };
      setMessage({
        type: 'error',
        text: ax.response?.data?.detail || 'Could not remove appointment.',
      });
    } finally {
      setProcessing(null);
    }
  };

  const handleReject = async (request: AppointmentRequest) => {
    if (!window.confirm(`Are you sure you want to reject this appointment request from ${request.user_name}?`)) {
      return;
    }

    setProcessing(request.request_id);

    try {
      const response = await fetch(`/api/appointment-requests/${request.request_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: 'REJECTED',
        }),
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Appointment rejected' });
        setTimeout(() => {
          fetchAppointmentRequests();
          setMessage({ type: '', text: '' });
        }, 1500);
      } else {
        const data = await response.json();
        setMessage({ type: 'error', text: data.detail || 'Failed to reject appointment' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Connection error. Please try again.' });
    } finally {
      setProcessing(null);
    }
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      PENDING: {
        color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        icon: <AlertCircle className="w-4 h-4" />,
      },
      ACCEPTED: {
        color: 'bg-green-100 text-green-800 border-green-300',
        icon: <CheckCircle className="w-4 h-4" />,
      },
      REJECTED: {
        color: 'bg-red-100 text-red-800 border-red-300',
        icon: <XCircle className="w-4 h-4" />,
      },
    };

    const badge = badges[status as keyof typeof badges];
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${badge.color}`}>
        {badge.icon}
        <span className="ml-2">{status}</span>
      </span>
    );
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (userType === 'DOCTOR') {
    const pendingRequests = appointmentRequests.filter(req => req.status === 'PENDING');
    const acceptedRequests = appointmentRequests.filter(req => req.status === 'ACCEPTED');

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-800 mb-2">Appointment Requests</h1>
              <p className="text-gray-600">Manage your patient appointments</p>
            </div>
            <button
              onClick={() => fetchAppointmentRequests()}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {message.text && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-4 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            {message.text}
          </motion.div>
        )}

        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
            <AlertCircle className="w-6 h-6 text-yellow-600 mr-2" />
            Pending Requests ({pendingRequests.length})
          </h2>

          {pendingRequests.length === 0 ? (
            <div className="text-center py-12">
              <AlertCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No pending appointment requests</p>
            </div>
          ) : (
            <div className="space-y-4">
              {pendingRequests.map((request) => (
                <motion.div
                  key={request.request_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <User className="w-5 h-5 text-blue-600 mr-2" />
                        <h3 className="text-lg font-semibold text-gray-800">{request.user_name}</h3>
                        <span className="ml-3 text-sm text-gray-500">({request.user_id})</span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                        <div className="flex items-center text-gray-600">
                          <Calendar className="w-4 h-4 mr-2" />
                          <span className="text-sm">
                            {request.preferred_date ? formatDate(request.preferred_date) : 'Not specified'}
                          </span>
                        </div>
                        <div className="flex items-center text-gray-600">
                          <Clock className="w-4 h-4 mr-2" />
                          <span className="text-sm">{request.preferred_time || 'Not specified'}</span>
                        </div>
                      </div>

                      <div className="bg-gray-50 rounded-lg p-3 mb-3">
                        <p className="text-sm font-medium text-gray-700 mb-1">Reason:</p>
                        <p className="text-sm text-gray-600">{request.reason || 'No reason provided'}</p>
                      </div>

                      <p className="text-xs text-gray-500">
                        Requested: {formatDateTime(request.created_at)}
                      </p>
                    </div>

                    <div className="flex flex-col space-y-2 ml-4">
                      <button
                        onClick={() => handleAccept(request)}
                        disabled={processing === request.request_id}
                        className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all disabled:opacity-50"
                      >
                        {processing === request.request_id ? (
                          <Loader className="w-4 h-4 animate-spin" />
                        ) : (
                          <>
                            <CheckCircle className="w-4 h-4 mr-2" />
                            Accept
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => handleReject(request)}
                        disabled={processing === request.request_id}
                        className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all disabled:opacity-50"
                      >
                        {processing === request.request_id ? (
                          <Loader className="w-4 h-4 animate-spin" />
                        ) : (
                          <>
                            <XCircle className="w-4 h-4 mr-2" />
                            Reject
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
            <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
            Accepted Appointments ({acceptedRequests.length})
          </h2>

          {acceptedRequests.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">No accepted appointments yet</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {acceptedRequests.map((request) => (
                <motion.div
                  key={request.request_id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="border border-green-200 bg-green-50 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-800">{request.user_name}</h3>
                    {getStatusBadge(request.status)}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{request.reason}</p>
                  <div className="text-sm text-gray-600 mb-2">
                    <Calendar className="w-4 h-4 inline mr-1" />
                    {request.preferred_date ? formatDate(request.preferred_date) : 'Not specified'} at {request.preferred_time}
                  </div>
                  {request.meet_link && (
                    <div className="mt-3 pt-3 border-t border-green-300 space-y-2">
                      <a
                        href={request.meet_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-center w-full px-4 py-2 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-all shadow-md hover:shadow-lg"
                      >
                        <Video className="w-5 h-5 mr-2" />
                        Join Video Consultation
                      </a>
                      <p className="text-xs text-gray-600 mt-2 text-center">
                        Meeting room: {request.meet_link.split('/').pop()}
                      </p>
                    </div>
                  )}
                  <button
                    type="button"
                    onClick={() => handleConsultationComplete(request)}
                    disabled={processing === request.request_id}
                    className="mt-3 flex items-center justify-center w-full px-4 py-2 border border-gray-300 text-gray-800 font-medium rounded-lg hover:bg-gray-100 transition-all disabled:opacity-50"
                  >
                    {processing === request.request_id ? (
                      <Loader className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <Trash2 className="w-4 h-4 mr-2" />
                        Consultation complete — remove appointment
                      </>
                    )}
                  </button>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">My Appointments</h1>
        <p className="text-gray-600">View your appointment requests and their status</p>
      </div>

      {userRequests.length === 0 ? (
        <div className="bg-white rounded-xl shadow-lg p-12 text-center">
          <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-700 mb-2">No Appointments Yet</h2>
          <p className="text-gray-500 mb-4">You haven't requested any appointments</p>
          <a
            href="/home"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-all"
          >
            Browse Doctors
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {userRequests.map((request) => (
            <motion.div
              key={request.request_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-xl shadow-lg p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-800">{request.doctor_name}</h3>
                  <p className="text-sm text-gray-500">{request.doctor_id}</p>
                </div>
                {getStatusBadge(request.status)}
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex items-center text-gray-600">
                  <Calendar className="w-5 h-5 mr-2" />
                  <span>{request.preferred_date ? formatDate(request.preferred_date) : 'Not specified'}</span>
                </div>
                <div className="flex items-center text-gray-600">
                  <Clock className="w-5 h-5 mr-2" />
                  <span>{request.preferred_time || 'Not specified'}</span>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-3 mb-4">
                <p className="text-sm font-medium text-gray-700 mb-1">Reason:</p>
                <p className="text-sm text-gray-600">{request.reason || 'No reason provided'}</p>
              </div>

              {request.status === 'ACCEPTED' && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4 space-y-3">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-semibold text-green-800">✓ Appointment Confirmed</span>
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  </div>
                  {request.meet_link && (
                    <>
                      <a
                        href={request.meet_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-center w-full py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
                      >
                        <Video className="w-5 h-5 mr-2" />
                        Join Video Consultation
                      </a>
                      <p className="text-xs text-gray-600 mt-2 text-center">
                        Room: {request.meet_link.split('/').pop()}
                      </p>
                    </>
                  )}
                  <button
                    type="button"
                    onClick={() => handleConsultationComplete(request)}
                    disabled={processing === request.request_id}
                    className="flex items-center justify-center w-full py-2 border border-gray-300 text-gray-800 font-medium rounded-lg hover:bg-white transition-all disabled:opacity-50 text-sm"
                  >
                    {processing === request.request_id ? (
                      <Loader className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <Trash2 className="w-4 h-4 mr-2" />
                        Consultation complete — remove appointment
                      </>
                    )}
                  </button>
                </div>
              )}

              {request.status === 'PENDING' && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                  <div className="flex items-center">
                    <AlertCircle className="w-5 h-5 text-yellow-600 mr-2" />
                    <span className="text-sm text-yellow-800 font-medium">
                      Waiting for doctor's confirmation
                    </span>
                  </div>
                </div>
              )}

              {request.status === 'REJECTED' && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
                  <div className="flex items-center">
                    <XCircle className="w-5 h-5 text-red-600 mr-2" />
                    <span className="text-sm text-red-800 font-medium">
                      Appointment was not accepted
                    </span>
                  </div>
                </div>
              )}

              <p className="text-xs text-gray-500 mt-4">
                Requested: {formatDateTime(request.created_at)}
              </p>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default VideoConsultation;
