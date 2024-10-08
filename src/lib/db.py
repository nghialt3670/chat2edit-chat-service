from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from models.chat import Chat
from models.phase import ChatPhase
from utils.env import ENV

client = AsyncIOMotorClient(ENV.MONGO_URI)
db = client.get_database()


def get_db():
    return db


async def init_db():
    await init_beanie(database=client.get_database(), document_models=[Chat, ChatPhase])
