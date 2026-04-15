"""
LiveKit voice agent: Deepgram STT/TTS, Hugging Face Inference (Llama) LLM, Silero VAD.

LLM uses the same Hub model + token as huggingface_hub.InferenceClient; LiveKit streams
via the OpenAI-compatible Inference router (see VOICE_HF_BASE_URL).

Compatible with livekit-agents 1.2.x (WorkerOptions + entrypoint_fnc).

Run from the backend directory:
  python -m voice_agent.worker dev

Download plugin assets:
  python -m voice_agent.worker download-files
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions
from livekit.plugins import deepgram, openai, silero

from voice_agent.constants import MEDICAL_VOICE_AGENT_NAME

_backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_backend_root, ".env"))
load_dotenv()

DEFAULT_HF_VOICE_MODEL = "meta-llama/Llama-3.3-70B-Instruct"
DEFAULT_HF_ROUTER_BASE = "https://router.huggingface.co/v1"

MEDICAL_VOICE_INSTRUCTIONS = """You are a supportive medical voice assistant for a multi-agent healthcare app.
You help with general wellness, mental health coping strategies, and explaining medical concepts in plain language.
You are not a licensed clinician: never give a definitive diagnosis, prescription, or treatment plan.
For emergencies or severe symptoms, urge the user to seek in-person or emergency care immediately.
Keep spoken answers concise, warm, and easy to follow without markdown or special symbols."""


class MedicalVoiceAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=MEDICAL_VOICE_INSTRUCTIONS)


def _voice_llm():
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
    if not token:
        raise RuntimeError(
            "HF_TOKEN (or HUGGINGFACE_HUB_TOKEN) is required for the voice LLM. "
            "Create a token at https://huggingface.co/settings/tokens with Inference access."
        )
    model = os.getenv("VOICE_HF_MODEL", "").strip() or DEFAULT_HF_VOICE_MODEL
    base_url = os.getenv("VOICE_HF_BASE_URL", "").strip() or DEFAULT_HF_ROUTER_BASE

    client = InferenceClient(model=model, token=token)
    return openai.LLM(model=client.model or model, base_url=base_url, api_key=token)


async def medical_voice_entrypoint(ctx: JobContext) -> None:
    ctx.log_context_fields = {"room": ctx.room.name}

    dg_key = os.getenv("DEEPGRAM_API_KEY")
    if not dg_key:
        raise RuntimeError("DEEPGRAM_API_KEY is not set")

    session = AgentSession(
        stt=deepgram.STT(model="nova-2", api_key=dg_key),
        llm=_voice_llm(),
        tts=deepgram.TTS(model="aura-asteria-en", api_key=dg_key),
        vad=silero.VAD.load(),
    )

    await session.start(agent=MedicalVoiceAssistant(), room=ctx.room)
    if os.getenv("VOICE_SKIP_GREETING", "").strip().lower() not in ("1", "true", "yes"):
        session.generate_reply(
            instructions=(
                "Greet the user briefly, then ask how you can help with their health, "
                "wellness, or mental health today."
            )
        )


if __name__ == "__main__":
    agents.cli.run_app(
        WorkerOptions(
            entrypoint_fnc=medical_voice_entrypoint,
            agent_name=MEDICAL_VOICE_AGENT_NAME,
        )
    )
