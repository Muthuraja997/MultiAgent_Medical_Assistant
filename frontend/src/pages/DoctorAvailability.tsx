import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Stethoscope, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { api } from '../services/api';

/**
 * Doctors toggle accepting new appointments / visibility as "available" in the system.
 */
const DoctorAvailability = () => {
  const [userType] = useState(() => localStorage.getItem('user_type'));
  const [doctorId] = useState(() => localStorage.getItem('user_id') || '');
  const [available, setAvailable] = useState(false);
  const [docName, setDocName] = useState('');
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [message, setMessage] = useState<{ type: 'ok' | 'err'; text: string } | null>(null);

  const isDoctor = userType === 'DOCTOR';

  useEffect(() => {
    if (!isDoctor || !doctorId) {
      setLoading(false);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const data = await api.getDoctor(doctorId);
        if (!cancelled) {
          setAvailable(Boolean(data.available_status));
          setDocName(data.doc_name || '');
        }
      } catch {
        if (!cancelled) setMessage({ type: 'err', text: 'Could not load your profile.' });
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [isDoctor, doctorId]);

  const updateStatus = async (next: boolean) => {
    setUpdating(true);
    setMessage(null);
    try {
      await api.updateDoctorAvailability(doctorId, next);
      setAvailable(next);
      setMessage({
        type: 'ok',
        text: next ? 'You are now marked as available.' : 'You are now marked as unavailable.',
      });
    } catch {
      setMessage({ type: 'err', text: 'Failed to update status. Try again.' });
    } finally {
      setUpdating(false);
    }
  };

  if (!isDoctor) {
    return (
      <div className="max-w-xl mx-auto p-8 text-center text-slate-600">
        This page is only for doctor accounts. Log in as a doctor to update availability.
      </div>
    );
  }

  if (!doctorId) {
    return (
      <div className="max-w-xl mx-auto p-8 text-center text-slate-600">
        Not signed in. Please log in again.
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-morphism rounded-2xl p-8 border border-slate-200/80"
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
            <Stethoscope className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800 font-display">Practice availability</h1>
            <p className="text-sm text-slate-600">{docName || doctorId}</p>
          </div>
        </div>

        <p className="text-slate-600 text-sm mb-6">
          When <strong>available</strong>, patients can see you as an option for appointments. Turn off when you are
          not taking new requests.
        </p>

        {loading ? (
          <div className="flex items-center justify-center py-12 text-slate-500">
            <Loader2 className="w-8 h-8 animate-spin mr-2" />
            Loading…
          </div>
        ) : (
          <div className="space-y-4">
            <div
              className={`flex items-center justify-between rounded-xl px-4 py-3 border-2 ${
                available ? 'border-emerald-200 bg-emerald-50/80' : 'border-slate-200 bg-slate-50'
              }`}
            >
              <div className="flex items-center gap-2">
                {available ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                ) : (
                  <XCircle className="w-5 h-5 text-slate-500" />
                )}
                <span className="font-medium text-slate-800">
                  Current status: {available ? 'Available (on)' : 'Unavailable (off)'}
                </span>
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                disabled={updating || available}
                onClick={() => updateStatus(true)}
                className="flex-1 min-w-[140px] py-3 px-4 rounded-xl font-semibold text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:shadow-lg disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                Update status: On
              </button>
              <button
                type="button"
                disabled={updating || !available}
                onClick={() => updateStatus(false)}
                className="flex-1 min-w-[140px] py-3 px-4 rounded-xl font-semibold text-white bg-gradient-to-r from-slate-600 to-slate-800 hover:shadow-lg disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                Update status: Off
              </button>
            </div>
          </div>
        )}

        {message && (
          <p
            className={`mt-4 text-sm font-medium ${message.type === 'ok' ? 'text-emerald-700' : 'text-red-600'}`}
            role="status"
          >
            {message.text}
          </p>
        )}
      </motion.div>
    </div>
  );
};

export default DoctorAvailability;
