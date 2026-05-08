import asyncio
import sys
import os
from httpx import AsyncClient

sys.path.append(os.getcwd())

async def run_tests():
    from main import app
    async with AsyncClient(app=app, base_url="http://test") as ac:
        print("Starting tests...")
        
        # Test teachers, then student for /my schedule
        logins = [
            {"email": "anna.ivanova@abc-school.ru", "password": "teacher123"},
            {"email": "kirill.smirnov@abc-school.ru", "password": "student123"}
        ]
        
        for creds in logins:
            print(f"Testing with {creds['email']}...")
            login_resp = await ac.post("/api/v1/auth/login", json=creds)
            if login_resp.status_code != 200:
                print(f"  Login failed ({login_resp.status_code}): {login_resp.text}")
                continue
            
            token = login_resp.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            endpoints = ["/api/v1/teachers", "/api/v1/users/me", "/api/v1/students", "/api/v1/schedule", "/api/v1/schedule/my"]
            for ep in endpoints:
                r = await ac.get(ep, headers=headers)
                print(f"  GET {ep} - {r.status_code}")
                if r.status_code == 200:
                  print(f"    Data: {r.text[:50]}...")
                else:
                  print(f"    Err: {r.text}")

if __name__ == "__main__":
    asyncio.run(run_tests())
