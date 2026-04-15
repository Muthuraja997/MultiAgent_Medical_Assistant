import { useEffect, useState } from 'react';
import type { Room } from 'livekit-client';
import { RoomEvent } from 'livekit-client';

/** Tracks whether the local user or a remote participant (agent) is in LiveKit active speakers. */
export function useVoiceSpeakingState(room: Room | undefined) {
  const [userSpeaking, setUserSpeaking] = useState(false);
  const [agentSpeaking, setAgentSpeaking] = useState(false);

  useEffect(() => {
    if (!room) return;

    const update = () => {
      const speakers = room.activeSpeakers;
      const localSid = room.localParticipant.sid;
      setUserSpeaking(speakers.some((p) => p.sid === localSid));
      setAgentSpeaking(speakers.some((p) => p.sid !== localSid));
    };

    room.on(RoomEvent.ActiveSpeakersChanged, update);
    update();

    return () => {
      room.off(RoomEvent.ActiveSpeakersChanged, update);
    };
  }, [room]);

  return { userSpeaking, agentSpeaking };
}
