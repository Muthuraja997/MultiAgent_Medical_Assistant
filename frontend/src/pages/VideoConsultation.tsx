import { useState, useEffect } from 'react';
import { Video, Calendar, Clock, Copy, Check, ExternalLink, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Meeting {
  id: string;
  roomName: string;
  doctorName: string;
  patientName: string;
  scheduledTime: string;
  status: 'scheduled' | 'active' | 'completed';
  duration?: number;
}

const VideoConsultation = () => {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [activeMeeting, setActiveMeeting] = useState<Meeting | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);
  const [newMeeting, setNewMeeting] = useState({
    doctorName: '',
    patientName: '',
    scheduledTime: '',
  });

  // Load Jitsi API script
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://meet.jit.si/external_api.js';
    script.async = true;
    document.head.appendChild(script);

    return () => {
      document.head.removeChild(script);
    };
  }, []);

  // Load saved meetings from localStorage
  useEffect(() => {
    const savedMeetings = localStorage.getItem('medicalMeetings');
    if (savedMeetings) {
      setMeetings(JSON.parse(savedMeetings));
    }
  }, []);

  // Save meetings to localStorage
  const saveMeetings = (updatedMeetings: Meeting[]) => {
    setMeetings(updatedMeetings);
    localStorage.setItem('medicalMeetings', JSON.stringify(updatedMeetings));
  };

  // Generate unique room name
  const generateRoomName = () => {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 8);
    return `medical-consult-${timestamp}-${random}`;
  };

  // Create new meeting
  const createMeeting = () => {
    if (!newMeeting.doctorName || !newMeeting.patientName || !newMeeting.scheduledTime) {
      alert('Please fill in all fields');
      return;
    }

    const meeting: Meeting = {
      id: Date.now().toString(),
      roomName: generateRoomName(),
      doctorName: newMeeting.doctorName,
      patientName: newMeeting.patientName,
      scheduledTime: newMeeting.scheduledTime,
      status: 'scheduled',
    };

    saveMeetings([...meetings, meeting]);
    setShowCreateModal(false);
    setNewMeeting({ doctorName: '', patientName: '', scheduledTime: '' });
  };

  // Start instant meeting
  const startInstantMeeting = () => {
    const meeting: Meeting = {
      id: Date.now().toString(),
      roomName: generateRoomName(),
      doctorName: 'Doctor',
      patientName: 'Patient',
      scheduledTime: new Date().toISOString(),
      status: 'active',
    };

    saveMeetings([...meetings, meeting]);
    setActiveMeeting(meeting);
  };

  // Join meeting
  const joinMeeting = (meeting: Meeting) => {
    const updatedMeetings = meetings.map(m =>
      m.id === meeting.id ? { ...m, status: 'active' as const } : m
    );
    saveMeetings(updatedMeetings);
    setActiveMeeting({ ...meeting, status: 'active' });
  };

  // End meeting
  const endMeeting = () => {
    if (activeMeeting) {
      const updatedMeetings = meetings.map(m =>
        m.id === activeMeeting.id ? { ...m, status: 'completed' as const } : m
      );
      saveMeetings(updatedMeetings);
    }
    setActiveMeeting(null);
  };

  // Copy meeting link
  const copyMeetingLink = (roomName: string) => {
    const link = `https://meet.jit.si/${roomName}`;
    navigator.clipboard.writeText(link);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  // Get meeting link
  const getMeetingLink = (roomName: string) => {
    return `https://meet.jit.si/${roomName}`;
  };

  // Format date/time
  const formatDateTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Delete meeting
  const deleteMeeting = (meetingId: string) => {
    const updatedMeetings = meetings.filter(m => m.id !== meetingId);
    saveMeetings(updatedMeetings);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white shadow-xl"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Video Consultation</h1>
            <p className="text-blue-100">Connect with doctors via secure video calls</p>
          </div>
          <Video className="w-16 h-16 opacity-50" />
        </div>
      </motion.div>

      {/* Active Meeting - Full Screen */}
      <AnimatePresence>
        {activeMeeting && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-gray-900"
          >
            <div className="h-full flex flex-col">
              {/* Meeting Header */}
              <div className="bg-gray-800 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                    <span className="text-white font-medium">Live Consultation</span>
                  </div>
                  <div className="text-gray-300 text-sm">
                    {activeMeeting.doctorName} • {activeMeeting.patientName}
                  </div>
                </div>
                <button
                  onClick={endMeeting}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
                >
                  <X className="w-5 h-5" />
                  End Call
                </button>
              </div>

              {/* Jitsi Meet Container */}
              <div className="flex-1">
                <iframe
                  src={`https://meet.jit.si/${activeMeeting.roomName}?userInfo.displayName=${activeMeeting.patientName}`}
                  allow="camera; microphone; fullscreen; display-capture"
                  style={{ width: '100%', height: '100%', border: 'none' }}
                  title="Video Consultation"
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quick Actions */}
      {!activeMeeting && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-4"
        >
          <button
            onClick={startInstantMeeting}
            className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-blue-500 group"
          >
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <Video className="w-8 h-8 text-white" />
              </div>
              <div className="text-left flex-1">
                <h3 className="text-xl font-bold text-gray-900 mb-1">Start Instant Meeting</h3>
                <p className="text-gray-600">Begin a consultation right now</p>
              </div>
            </div>
          </button>

          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-green-500 group"
          >
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-teal-500 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                <Calendar className="w-8 h-8 text-white" />
              </div>
              <div className="text-left flex-1">
                <h3 className="text-xl font-bold text-gray-900 mb-1">Schedule Meeting</h3>
                <p className="text-gray-600">Plan a consultation for later</p>
              </div>
            </div>
          </button>
        </motion.div>
      )}

      {/* Meetings List */}
      {!activeMeeting && meetings.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-lg p-6"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Your Consultations</h2>

          <div className="space-y-4">
            {meetings.map((meeting) => (
              <motion.div
                key={meeting.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={`p-4 border-2 rounded-xl transition-all duration-300 ${
                  meeting.status === 'active'
                    ? 'border-green-500 bg-green-50'
                    : meeting.status === 'completed'
                    ? 'border-gray-300 bg-gray-50'
                    : 'border-blue-300 bg-blue-50 hover:border-blue-500'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          meeting.status === 'active'
                            ? 'bg-green-500 text-white'
                            : meeting.status === 'completed'
                            ? 'bg-gray-500 text-white'
                            : 'bg-blue-500 text-white'
                        }`}
                      >
                        {meeting.status.charAt(0).toUpperCase() + meeting.status.slice(1)}
                      </span>
                      <h3 className="font-semibold text-gray-900">
                        {meeting.doctorName} & {meeting.patientName}
                      </h3>
                    </div>

                    <div className="space-y-1 text-sm text-gray-600 ml-0">
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4" />
                        <span>{formatDateTime(meeting.scheduledTime)}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <ExternalLink className="w-4 h-4" />
                        <a
                          href={getMeetingLink(meeting.roomName)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          {getMeetingLink(meeting.roomName)}
                        </a>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    {meeting.status !== 'completed' && (
                      <>
                        <button
                          onClick={() => copyMeetingLink(meeting.roomName)}
                          className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center gap-2"
                          title="Copy meeting link"
                        >
                          {copiedLink ? (
                            <Check className="w-4 h-4 text-green-600" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </button>
                        <button
                          onClick={() => joinMeeting(meeting)}
                          className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all duration-300 flex items-center gap-2"
                        >
                          <Video className="w-4 h-4" />
                          Join
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => deleteMeeting(meeting.id)}
                      className="px-3 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
                      title="Delete meeting"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Empty State */}
      {!activeMeeting && meetings.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-xl shadow-lg p-12 text-center"
        >
          <Video className="w-20 h-20 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">No Consultations Yet</h3>
          <p className="text-gray-600 mb-6">Start an instant meeting or schedule one for later</p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={startInstantMeeting}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all duration-300"
            >
              Start Now
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 rounded-lg hover:border-gray-400 transition-colors"
            >
              Schedule
            </button>
          </div>
        </motion.div>
      )}

      {/* Create Meeting Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4"
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Schedule Consultation</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Doctor Name
                  </label>
                  <input
                    type="text"
                    value={newMeeting.doctorName}
                    onChange={(e) =>
                      setNewMeeting({ ...newMeeting, doctorName: e.target.value })
                    }
                    placeholder="Dr. Smith"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Patient Name
                  </label>
                  <input
                    type="text"
                    value={newMeeting.patientName}
                    onChange={(e) =>
                      setNewMeeting({ ...newMeeting, patientName: e.target.value })
                    }
                    placeholder="John Doe"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Scheduled Time
                  </label>
                  <input
                    type="datetime-local"
                    value={newMeeting.scheduledTime}
                    onChange={(e) =>
                      setNewMeeting({ ...newMeeting, scheduledTime: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={createMeeting}
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all duration-300"
                >
                  Create Meeting
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default VideoConsultation;
