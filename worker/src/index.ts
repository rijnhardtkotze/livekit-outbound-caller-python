import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { AgentDispatchClient, RoomServiceClient } from 'livekit-server-sdk';

type Bindings = {
  LIVEKIT_URL: string;
  LIVEKIT_API_KEY: string;
  LIVEKIT_API_SECRET: string;
  SIP_OUTBOUND_TRUNK_ID: string;
};

const app = new Hono<{ Bindings: Bindings }>();

// Enable CORS for API routes
app.use('/api/*', cors());

// Health check endpoint
app.get('/api/health', (c) => {
  return c.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Dispatch an outbound call
app.post('/api/dispatch', async (c) => {
  const { LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET } = c.env;

  if (!LIVEKIT_URL || !LIVEKIT_API_KEY || !LIVEKIT_API_SECRET) {
    return c.json(
      { error: 'Missing LiveKit configuration. Please set LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET.' },
      500
    );
  }

  let body: { phoneNumber?: string; transferTo?: string };
  try {
    body = await c.req.json();
  } catch {
    return c.json({ error: 'Invalid JSON body' }, 400);
  }

  const { phoneNumber, transferTo } = body;

  if (!phoneNumber) {
    return c.json({ error: 'phoneNumber is required' }, 400);
  }

  // Clean the phone number (remove formatting characters)
  const cleanedPhone = phoneNumber.replace(/[\s\-()]/g, '');

  // Validate phone number format (E.164 format: + followed by 1-15 digits)
  // Allows country codes starting with any digit (e.g., +33 for France, +1 for US)
  const phoneRegex = /^\+?[0-9]{1,15}$/;
  if (!phoneRegex.test(cleanedPhone)) {
    return c.json({ error: 'Invalid phone number format. Use E.164 format (e.g., +1234567890)' }, 400);
  }

  try {
    // Create a unique room name for this call using crypto.randomUUID for better uniqueness
    const roomName = `outbound-call-${Date.now()}-${crypto.randomUUID().slice(0, 8)}`;

    // Create the room first
    const roomService = new RoomServiceClient(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET);
    await roomService.createRoom({
      name: roomName,
      emptyTimeout: 300, // 5 minutes
      maxParticipants: 10,
    });

    // Dispatch the agent with metadata containing the phone number info
    const agentDispatch = new AgentDispatchClient(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET);

    const metadata = JSON.stringify({
      phone_number: cleanedPhone,
      transfer_to: transferTo ? transferTo.replace(/[\s\-()]/g, '') : '',
    });

    const dispatch = await agentDispatch.createDispatch(roomName, 'outbound-caller', {
      metadata,
    });

    return c.json({
      success: true,
      roomName,
      dispatchId: dispatch.id,
      phoneNumber,
      transferTo: transferTo || null,
      message: 'Call dispatched successfully. The agent will dial the number.',
    });
  } catch (error) {
    console.error('Error dispatching call:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return c.json(
      { error: 'Failed to dispatch call', details: errorMessage },
      500
    );
  }
});

// List active dispatches for a room
app.get('/api/dispatch/:roomName', async (c) => {
  const { LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET } = c.env;

  if (!LIVEKIT_URL || !LIVEKIT_API_KEY || !LIVEKIT_API_SECRET) {
    return c.json(
      { error: 'Missing LiveKit configuration' },
      500
    );
  }

  const roomName = c.req.param('roomName');

  try {
    const agentDispatch = new AgentDispatchClient(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET);
    const dispatches = await agentDispatch.listDispatch(roomName);

    return c.json({
      roomName,
      dispatches: dispatches.map((d) => ({
        id: d.id,
        agentName: d.agentName,
        state: d.state,
      })),
    });
  } catch (error) {
    console.error('Error listing dispatches:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return c.json(
      { error: 'Failed to list dispatches', details: errorMessage },
      500
    );
  }
});

// List active rooms
app.get('/api/rooms', async (c) => {
  const { LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET } = c.env;

  if (!LIVEKIT_URL || !LIVEKIT_API_KEY || !LIVEKIT_API_SECRET) {
    return c.json(
      { error: 'Missing LiveKit configuration' },
      500
    );
  }

  try {
    const roomService = new RoomServiceClient(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET);
    const rooms = await roomService.listRooms();

    return c.json({
      rooms: rooms.map((room) => ({
        name: room.name,
        numParticipants: room.numParticipants,
        creationTime: room.creationTime,
      })),
    });
  } catch (error) {
    console.error('Error listing rooms:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return c.json(
      { error: 'Failed to list rooms', details: errorMessage },
      500
    );
  }
});

export default app;
