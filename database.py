from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME, OWNER_IDS

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

sources_col = db["sources"]      # one doc per source channel
sudo_col = db["sudo_users"]      # extra sudo users beyond OWNER_IDS
stats_col = db["stats"]          # single doc, global counters


# ---------- Sources / targets / config ----------

async def add_source(source_id: int, name: str = ""):
    doc = {
        "_id": source_id,
        "name": name,
        "targets": [],
        "mode": "clean",          # clean | copy
        "filter_type": "all",     # all | media | text
        "blacklist": [],
        "active": True,
    }
    await sources_col.update_one(
        {"_id": source_id}, {"$setOnInsert": doc}, upsert=True
    )


async def remove_source(source_id: int):
    result = await sources_col.delete_one({"_id": source_id})
    return result.deleted_count > 0


async def get_source(source_id: int):
    return await sources_col.find_one({"_id": source_id})


async def get_all_sources():
    return [doc async for doc in sources_col.find({})]


async def get_active_sources():
    return [doc async for doc in sources_col.find({"active": True})]


async def add_target(source_id: int, target_id: int):
    result = await sources_col.update_one(
        {"_id": source_id}, {"$addToSet": {"targets": target_id}}
    )
    return result.modified_count > 0


async def remove_target(source_id: int, target_id: int):
    result = await sources_col.update_one(
        {"_id": source_id}, {"$pull": {"targets": target_id}}
    )
    return result.modified_count > 0


async def deactivate_target(source_id: int, target_id: int):
    """Used when bot gets kicked/removed from a target chat."""
    await sources_col.update_one(
        {"_id": source_id}, {"$pull": {"targets": target_id}}
    )


async def set_mode(source_id: int, mode: str):
    await sources_col.update_one({"_id": source_id}, {"$set": {"mode": mode}})


async def set_filter(source_id: int, filter_type: str):
    await sources_col.update_one(
        {"_id": source_id}, {"$set": {"filter_type": filter_type}}
    )


async def add_blacklist_word(source_id: int, word: str):
    await sources_col.update_one(
        {"_id": source_id}, {"$addToSet": {"blacklist": word.lower()}}
    )


async def remove_blacklist_word(source_id: int, word: str):
    await sources_col.update_one(
        {"_id": source_id}, {"$pull": {"blacklist": word.lower()}}
    )


async def set_active(source_id: int, active: bool):
    await sources_col.update_one({"_id": source_id}, {"$set": {"active": active}})


# ---------- Sudo users ----------

async def add_sudo(user_id: int):
    await sudo_col.update_one(
        {"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True
    )


async def remove_sudo(user_id: int):
    result = await sudo_col.delete_one({"_id": user_id})
    return result.deleted_count > 0


async def list_sudo():
    return [doc["_id"] async for doc in sudo_col.find({})]


async def is_authorized(user_id: int) -> bool:
    if user_id in OWNER_IDS:
        return True
    doc = await sudo_col.find_one({"_id": user_id})
    return doc is not None


# ---------- Stats ----------

async def bump_stats(forwarded: int = 0, failed: int = 0):
    await stats_col.update_one(
        {"_id": "global"},
        {"$inc": {"forwarded": forwarded, "failed": failed}},
        upsert=True,
    )


async def get_stats():
    doc = await stats_col.find_one({"_id": "global"})
    if not doc:
        return {"forwarded": 0, "failed": 0}
    return doc
