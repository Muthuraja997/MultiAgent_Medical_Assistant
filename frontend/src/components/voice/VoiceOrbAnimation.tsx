import { motion, useReducedMotion } from 'framer-motion';

export type VoiceOrbAnimationProps = {
  userSpeaking: boolean;
  agentSpeaking: boolean;
};

/**
 * Siri-style multilayer orb: soft glow, expanding rings, color shifts for user vs assistant audio.
 */
export function VoiceOrbAnimation({ userSpeaking, agentSpeaking }: VoiceOrbAnimationProps) {
  const reduceMotion = useReducedMotion();
  const active = userSpeaking || agentSpeaking;
  const accent =
    userSpeaking && agentSpeaking ? 'both' : agentSpeaking ? 'agent' : userSpeaking ? 'user' : 'idle';

  const coreGradient =
    accent === 'both'
      ? 'radial-gradient(circle at 28% 32%, rgba(196, 181, 253, 0.95), rgba(56, 189, 248, 0.55), rgba(109, 40, 217, 0.85))'
      : accent === 'agent'
        ? 'radial-gradient(circle at 30% 30%, rgba(216, 180, 254, 0.95), rgba(139, 92, 246, 0.55), rgba(88, 28, 135, 0.85))'
        : accent === 'user'
          ? 'radial-gradient(circle at 35% 25%, rgba(165, 243, 252, 0.95), rgba(56, 189, 248, 0.6), rgba(14, 116, 144, 0.9))'
          : 'radial-gradient(circle at 40% 35%, rgba(196, 181, 253, 0.5), rgba(99, 102, 241, 0.35), rgba(30, 27, 75, 0.75))';

  const glowColor =
    accent === 'both'
      ? 'rgba(129, 140, 248, 0.5)'
      : accent === 'agent'
        ? 'rgba(167, 139, 250, 0.55)'
        : accent === 'user'
          ? 'rgba(34, 211, 238, 0.45)'
          : 'rgba(129, 140, 248, 0.25)';

  const ringDuration = reduceMotion ? 0 : active ? 1.35 : 3.2;
  const ringScale = reduceMotion ? 1 : active ? [1, 1.38, 1] : [1, 1.12, 1];
  const ringOpacity = reduceMotion ? 0.2 : active ? [0.35, 0.08, 0.35] : [0.2, 0.08, 0.2];

  const label = agentSpeaking && userSpeaking
    ? 'Conversation'
    : agentSpeaking
      ? 'Assistant speaking'
      : userSpeaking
        ? 'Listening…'
        : 'Ready';

  return (
    <div className="relative mx-auto flex w-full max-w-[280px] flex-col items-center">
      <div className="relative flex h-[220px] w-[220px] items-center justify-center">
        {/* Ambient glow */}
        <motion.div
          className="pointer-events-none absolute inset-0 rounded-full blur-3xl"
          style={{ background: glowColor }}
          animate={
            reduceMotion
              ? { opacity: active ? 0.5 : 0.25 }
              : { opacity: active ? [0.45, 0.75, 0.45] : [0.2, 0.32, 0.2], scale: active ? [1, 1.08, 1] : [1, 1.03, 1] }
          }
          transition={{ duration: active ? 1.2 : 3.5, repeat: reduceMotion ? 0 : Infinity, ease: 'easeInOut' }}
        />

        {/* Expanding rings */}
        {[0, 1, 2, 3].map((i) => (
          <motion.div
            key={i}
            className="pointer-events-none absolute rounded-full border border-white/25"
            style={{
              width: 100 + i * 28,
              height: 100 + i * 28,
            }}
            animate={
              reduceMotion
                ? { scale: 1, opacity: active ? 0.28 : 0.14 }
                : { scale: ringScale, opacity: ringOpacity }
            }
            transition={{
              duration: ringDuration,
              repeat: reduceMotion ? 0 : Infinity,
              ease: 'easeInOut',
              delay: reduceMotion ? 0 : i * 0.18,
            }}
          />
        ))}

        {/* Core orb */}
        <motion.div
          className="relative z-10 h-[100px] w-[100px] rounded-full shadow-[0_0_60px_rgba(139,92,246,0.35)]"
          style={{
            background: coreGradient,
            boxShadow:
              accent === 'both'
                ? '0 0 56px rgba(34, 211, 238, 0.35), 0 0 48px rgba(167, 139, 250, 0.4), inset 0 -12px 24px rgba(0,0,0,0.22)'
                : accent === 'user'
                  ? '0 0 48px rgba(34, 211, 238, 0.45), inset 0 -12px 24px rgba(0,0,0,0.2)'
                  : accent === 'agent'
                    ? '0 0 52px rgba(167, 139, 250, 0.5), inset 0 -12px 24px rgba(0,0,0,0.25)'
                    : '0 0 36px rgba(129, 140, 248, 0.25), inset 0 -8px 20px rgba(0,0,0,0.15)',
          }}
          animate={
            reduceMotion
              ? { scale: active ? 1.04 : 1 }
              : { scale: active ? [1, 1.06, 1] : [1, 1.02, 1] }
          }
          transition={{ duration: active ? 0.9 : 2.8, repeat: reduceMotion ? 0 : Infinity, ease: 'easeInOut' }}
        />

        {/* Inner specular highlight */}
        <div
          className="pointer-events-none absolute left-1/2 top-1/2 z-20 h-[52px] w-[52px] -translate-x-[65%] -translate-y-[70%] rounded-full opacity-40 blur-md"
          style={{
            background: 'radial-gradient(circle, rgba(255,255,255,0.85) 0%, transparent 70%)',
          }}
        />
      </div>

      <p className="mt-4 text-center text-sm font-medium tracking-wide text-slate-300">{label}</p>
    </div>
  );
}
