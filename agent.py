from __future__ import annotations

import asyncio
import logging
from dotenv import load_dotenv
import json
import os
from typing import Any

from livekit import rtc, api
from livekit.agents import (
    AgentSession,
    Agent,
    JobContext,
    function_tool,
    RunContext,
    get_job_context,
    cli,
    WorkerOptions,
    RoomInputOptions,
)
from livekit.plugins import (
    deepgram,
    openai,
    cartesia,
    silero,
    noise_cancellation,  # noqa: F401
)
from livekit.plugins.turn_detector.english import EnglishModel


# load environment variables, this is optional, only used for local development
load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("outbound-caller")
logger.setLevel(logging.INFO)

outbound_trunk_id = os.getenv("SIP_OUTBOUND_TRUNK_ID")

# Cloudflare configuration
use_cloudflare = os.getenv("USE_CLOUDFLARE", "false").lower() == "true"
cloudflare_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
cloudflare_api_token = os.getenv("CLOUDFLARE_API_TOKEN")
cloudflare_gateway_id = os.getenv("CLOUDFLARE_AI_GATEWAY_ID")
cloudflare_llm_model = os.getenv(
    "CLOUDFLARE_LLM_MODEL", "@cf/meta/llama-3.1-8b-instruct"
)


def get_llm():
    """Get the LLM instance based on configuration.

    Returns Cloudflare Workers AI LLM if USE_CLOUDFLARE=true,
    otherwise returns OpenAI LLM.
    """
    if (
        use_cloudflare
        and cloudflare_account_id
        and cloudflare_account_id.strip()
        and cloudflare_api_token
        and cloudflare_api_token.strip()
    ):
        logger.info(
            f"Using Cloudflare Workers AI LLM with model: {cloudflare_llm_model}"
        )
        # Cloudflare Workers AI provides OpenAI-compatible endpoints
        return openai.LLM(
            model=cloudflare_llm_model,
            base_url=f"https://api.cloudflare.com/client/v4/accounts/{cloudflare_account_id}/ai/v1",
            api_key=cloudflare_api_token,
        )
    else:
        logger.info("Using OpenAI LLM with model: gpt-4o")
        return openai.LLM(model="gpt-4o")


def get_stt():
    """Get the STT instance based on configuration.

    Returns Deepgram STT proxied through Cloudflare AI Gateway if configured,
    otherwise returns standard Deepgram STT.
    """
    if (
        use_cloudflare
        and cloudflare_account_id
        and cloudflare_account_id.strip()
        and cloudflare_gateway_id
        and cloudflare_gateway_id.strip()
    ):
        logger.info("Using Deepgram STT through Cloudflare AI Gateway")
        # Cloudflare AI Gateway can proxy Deepgram API requests
        # The gateway URL format: https://gateway.ai.cloudflare.com/v1/{account_id}/{gateway_id}/deepgram/v1/listen
        gateway_base_url = f"https://gateway.ai.cloudflare.com/v1/{cloudflare_account_id}/{cloudflare_gateway_id}/deepgram/v1/listen"
        return deepgram.STT(base_url=gateway_base_url)
    else:
        logger.info("Using Deepgram STT directly")
        return deepgram.STT()


def get_tts():
    """Get the TTS instance based on configuration.

    Returns Cartesia TTS proxied through Cloudflare AI Gateway if configured,
    otherwise returns standard Cartesia TTS.
    """
    if (
        use_cloudflare
        and cloudflare_account_id
        and cloudflare_account_id.strip()
        and cloudflare_gateway_id
        and cloudflare_gateway_id.strip()
    ):
        logger.info("Using Cartesia TTS through Cloudflare AI Gateway")
        # Cloudflare AI Gateway can proxy Cartesia API requests
        gateway_base_url = f"https://gateway.ai.cloudflare.com/v1/{cloudflare_account_id}/{cloudflare_gateway_id}/cartesia"
        return cartesia.TTS(base_url=gateway_base_url)
    else:
        logger.info("Using Cartesia TTS directly")
        return cartesia.TTS()


class OutboundCaller(Agent):
    def __init__(
        self,
        *,
        name: str,
        appointment_time: str,
        dial_info: dict[str, Any],
    ):
        super().__init__(
            instructions=f"""
            You are a scheduling assistant for a dental practice. Your interface with user will be voice.
            You will be on a call with a patient who has an upcoming appointment. Your goal is to confirm the appointment details.
            As a customer service representative, you will be polite and professional at all times. Allow user to end the conversation.

            When the user would like to be transferred to a human agent, first confirm with them. upon confirmation, use the transfer_call tool.
            The customer's name is {name}. His appointment is on {appointment_time}.
            """
        )
        # keep reference to the participant for transfers
        self.participant: rtc.RemoteParticipant | None = None

        self.dial_info = dial_info

    def set_participant(self, participant: rtc.RemoteParticipant):
        self.participant = participant

    async def hangup(self):
        """Helper function to hang up the call by deleting the room"""

        job_ctx = get_job_context()
        await job_ctx.api.room.delete_room(
            api.DeleteRoomRequest(
                room=job_ctx.room.name,
            )
        )

    @function_tool()
    async def transfer_call(self, ctx: RunContext):
        """Transfer the call to a human agent, called after confirming with the user"""

        transfer_to = self.dial_info["transfer_to"]
        if not transfer_to:
            return "cannot transfer call"

        logger.info(f"transferring call to {transfer_to}")

        # let the message play fully before transferring
        await ctx.session.generate_reply(
            instructions="let the user know you'll be transferring them"
        )

        job_ctx = get_job_context()
        try:
            await job_ctx.api.sip.transfer_sip_participant(
                api.TransferSIPParticipantRequest(
                    room_name=job_ctx.room.name,
                    participant_identity=self.participant.identity,
                    transfer_to=f"tel:{transfer_to}",
                )
            )

            logger.info(f"transferred call to {transfer_to}")
        except Exception as e:
            logger.error(f"error transferring call: {e}")
            await ctx.session.generate_reply(
                instructions="there was an error transferring the call."
            )
            await self.hangup()

    @function_tool()
    async def end_call(self, ctx: RunContext):
        """Called when the user wants to end the call"""
        logger.info(f"ending the call for {self.participant.identity}")

        # let the agent finish speaking
        current_speech = ctx.session.current_speech
        if current_speech:
            await current_speech.wait_for_playout()

        await self.hangup()

    @function_tool()
    async def look_up_availability(
        self,
        ctx: RunContext,
        date: str,
    ):
        """Called when the user asks about alternative appointment availability

        Args:
            date: The date of the appointment to check availability for
        """
        logger.info(
            f"looking up availability for {self.participant.identity} on {date}"
        )
        await asyncio.sleep(3)
        return {
            "available_times": ["1pm", "2pm", "3pm"],
        }

    @function_tool()
    async def confirm_appointment(
        self,
        ctx: RunContext,
        date: str,
        time: str,
    ):
        """Called when the user confirms their appointment on a specific date.
        Use this tool only when they are certain about the date and time.

        Args:
            date: The date of the appointment
            time: The time of the appointment
        """
        logger.info(
            f"confirming appointment for {self.participant.identity} on {date} at {time}"
        )
        return "reservation confirmed"

    @function_tool()
    async def detected_answering_machine(self, ctx: RunContext):
        """Called when the call reaches voicemail. Use this tool AFTER you hear the voicemail greeting"""
        logger.info(f"detected answering machine for {self.participant.identity}")
        await self.hangup()


async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect()

    # when dispatching the agent, we'll pass it the approriate info to dial the user
    # dial_info is a dict with the following keys:
    # - phone_number: the phone number to dial
    # - transfer_to: the phone number to transfer the call to when requested
    dial_info = json.loads(ctx.job.metadata)
    participant_identity = phone_number = dial_info["phone_number"]

    # look up the user's phone number and appointment details
    agent = OutboundCaller(
        name="Jayden",
        appointment_time="next Tuesday at 3pm",
        dial_info=dial_info,
    )

    # the following uses GPT-4o, Deepgram and Cartesia by default
    # or Cloudflare Workers AI, Deepgram via AI Gateway, and Cartesia via AI Gateway
    # when USE_CLOUDFLARE=true
    session = AgentSession(
        turn_detection=EnglishModel(),
        vad=silero.VAD.load(),
        stt=get_stt(),
        tts=get_tts(),
        llm=get_llm(),
        # you can also use a speech-to-speech model like OpenAI's Realtime API
        # llm=openai.realtime.RealtimeModel()
    )

    # start the session first before dialing, to ensure that when the user picks up
    # the agent does not miss anything the user says
    session_started = asyncio.create_task(
        session.start(
            agent=agent,
            room=ctx.room,
            room_input_options=RoomInputOptions(
                # enable Krisp background voice and noise removal
                noise_cancellation=noise_cancellation.BVCTelephony(),
            ),
        )
    )

    # `create_sip_participant` starts dialing the user
    try:
        await ctx.api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id=outbound_trunk_id,
                sip_call_to=phone_number,
                participant_identity=participant_identity,
                # function blocks until user answers the call, or if the call fails
                wait_until_answered=True,
            )
        )

        # wait for the agent session start and participant join
        await session_started
        participant = await ctx.wait_for_participant(identity=participant_identity)
        logger.info(f"participant joined: {participant.identity}")

        agent.set_participant(participant)

    except api.TwirpError as e:
        logger.error(
            f"error creating SIP participant: {e.message}, "
            f"SIP status: {e.metadata.get('sip_status_code')} "
            f"{e.metadata.get('sip_status')}"
        )
        ctx.shutdown()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="outbound-caller",
        )
    )
