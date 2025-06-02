import motor.motor_asyncio

MONGO_URI = "mongodb://hrms_us:hrms%40$8087@103.175.163.125:12109/hrms?authMechanism=DEFAULT"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

db = client.hrms