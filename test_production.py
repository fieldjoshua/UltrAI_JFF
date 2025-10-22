#!/usr/bin/env python3
"""Quick test of production deployment"""
import httpx
import asyncio
import time

BACKEND_URL = "https://ultrai-jff.onrender.com"

async def test_production():
    async with httpx.AsyncClient(timeout=300.0) as client:
        # 1. Test health
        print("Testing backend health...")
        health = await client.get(f"{BACKEND_URL}/health")
        print(f"Health: {health.status_code} - {health.json()}")

        # 2. Submit query
        print("\nSubmitting query...")
        response = await client.post(
            f"{BACKEND_URL}/runs",
            json={"query": "What is 2+2?", "cocktail": "SPEEDY"}
        )
        print(f"Submit response: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")

        if response.status_code != 200:
            print(f"ERROR: Failed to submit query")
            return

        run_id = data.get("run_id")
        print(f"Run ID: {run_id}")

        # 3. Poll for completion
        print("\nPolling for completion...")
        start = time.time()
        while time.time() - start < 180:
            status = await client.get(f"{BACKEND_URL}/runs/{run_id}/status")
            status_data = status.json()
            print(f"Status: {status_data}")

            if status_data.get("completed"):
                print(f"\n✅ COMPLETED in {time.time() - start:.1f}s")
                return

            await asyncio.sleep(5)

        print(f"\n❌ TIMEOUT after {time.time() - start:.1f}s")
        print(f"Last status: {status_data}")

if __name__ == "__main__":
    asyncio.run(test_production())
