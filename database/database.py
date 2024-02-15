import asyncpg
import os

# Connection string for PostgreSQL is provided by Replit as an environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

async def create_tables():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS guild_memberships (
        guild_id BIGINT PRIMARY KEY,
        membership_type TEXT CHECK (membership_type IN ('FREE', 'PAID')) DEFAULT 'FREE',
        membership_expiry_date BIGINT NULL,
        max_assistants INT NOT NULL
    );
    """)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS guild_assistants (
        assistant_id TEXT PRIMARY KEY,
        guild_id BIGINT,
        assistant_name TEXT,
        assistant_prompt TEXT,
        assistant_thread_id TEXT,
        assistant_channel BIGINT,
        FOREIGN KEY (guild_id) REFERENCES guild_memberships(guild_id)
    );
    """)
    await conn.close()

async def create_or_update_guild_membership(guild_id, membership_type='FREE', membership_expiry_date=None):
    max_assistants = 1 if membership_type == 'FREE' else 3
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        INSERT INTO guild_memberships (guild_id, membership_type, membership_expiry_date, max_assistants)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT(guild_id) DO UPDATE SET
        membership_type = EXCLUDED.membership_type,
        membership_expiry_date = EXCLUDED.membership_expiry_date,
        max_assistants = EXCLUDED.max_assistants;
    """, guild_id, membership_type, membership_expiry_date, max_assistants)
    await conn.close()

async def add_or_update_guild_assistant(assistant_id, guild_id, assistant_name, assistant_prompt, assistant_thread_id, assistant_channel):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        INSERT INTO guild_assistants (assistant_id, guild_id, assistant_name, assistant_prompt, assistant_thread_id, assistant_channel)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (assistant_id) 
        DO UPDATE SET 
            guild_id = EXCLUDED.guild_id,
            assistant_name = EXCLUDED.assistant_name,
            assistant_prompt = EXCLUDED.assistant_prompt, 
            assistant_thread_id = EXCLUDED.assistant_thread_id, 
            assistant_channel = EXCLUDED.assistant_channel;
    """, assistant_id, guild_id, assistant_name, assistant_prompt, assistant_thread_id, assistant_channel)
    await conn.close()

async def delete_guild_membership(guild_id):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        DELETE FROM guild_memberships WHERE guild_id = $1;
    """, guild_id)
    await conn.close()

async def delete_guild_assistant(assistant_id):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        DELETE FROM guild_assistants WHERE assistant_id = $1;
    """, assistant_id)
    await conn.close()

# New function to fetch guild membership details
async def fetch_guild_membership(guild_id):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("""
        SELECT guild_id, membership_type, membership_expiry_date, max_assistants
        FROM guild_memberships
        WHERE guild_id = $1;
    """, guild_id)
    await conn.close()
    if row:
        return {
            "guild_id": row["guild_id"],
            "membership_type": row["membership_type"],
            "membership_expiry_date": row["membership_expiry_date"],
            "max_assistants": row["max_assistants"]
        }
    else:
        return None

# New function to fetch all assistants by guild ID
async def fetch_assistants_by_guild(guild_id):
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("""
        SELECT assistant_id, guild_id, assistant_name, assistant_prompt, assistant_thread_id, assistant_channel
        FROM guild_assistants
        WHERE guild_id = $1;
    """, guild_id)
    await conn.close()

    assistants = [{
        "assistant_id": row["assistant_id"],
        "guild_id": row["guild_id"],
        "assistant_name": row["assistant_name"],
        "assistant_prompt": row["assistant_prompt"],
        "assistant_thread_id": row["assistant_thread_id"],
        "assistant_channel": row["assistant_channel"]
    } for row in rows]

    return assistants

# New function to fetch a specific assistant by assistant ID
async def fetch_assistant_by_id(assistant_id):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("""
        SELECT assistant_id, guild_id, assistant_name, assistant_prompt, assistant_thread_id, assistant_channel
        FROM guild_assistants
        WHERE assistant_id = $1;
    """, assistant_id)
    await conn.close()

    if row:
        return {
            "assistant_id": row["assistant_id"],
            "guild_id": row["guild_id"],
            "assistant_name": row["assistant_name"],
            "assistant_prompt": row["assistant_prompt"],
            "assistant_thread_id": row["assistant_thread_id"],
            "assistant_channel": row["assistant_channel"]
        }
    else:
        return None