import aioredis

class RedisRepository:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.from_url("redis://localhost", decode_responses=True)

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def save_todo(self, key, todo_data):
        todo_data['completed'] = int(todo_data['completed'])
        await self.redis.hset(key, mapping=todo_data)

    async def get_all_todos(self):
        keys = await self.redis.keys("todo:*")
        keys = [k for k in keys if 'counter' not in k]
        todos = []
        for key in keys:
            todo_data = await self.redis.hgetall(key)
            todos.append(todo_data)
        return todos

    async def get_todo_by_id(self, todo_id):
        return await self.redis.hgetall(f"todo:{todo_id}")

    async def update_todo(self, todo_id, updated_todo_data):
        if await self.redis.exists(f"todo:{todo_id}"):
            updated_todo_data['completed'] = int(updated_todo_data['completed'])
            await self.redis.hset(f"todo:{todo_id}", mapping=updated_todo_data)
            return True
        return False

    async def delete_todo(self, todo_id):
        return await self.redis.delete(f"todo:{todo_id}")
