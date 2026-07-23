from locust import HttpUser, task, between
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FINSIGHT_API_KEY")

class FinSightUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def ask_revenue(self):
        self.client.post("/query",
            json={"query": "What is Apple's total revenue in 2025?"},
            headers={"X-API-Key": API_KEY}
        )
    
    @task(3)
    def ask_applecare(self):
        self.client.post("/query",
            json={"query": "What is AppleCare?"},
            headers={"X-API-Key": API_KEY}
        )
    
    @task(2)
    def ask_iphone_revenue(self):
        self.client.post("/query",
            json={"query": "What was iPhone revenue in 2025?"},
            headers={"X-API-Key": API_KEY}
        )
    
    @task(2)
    def ask_risks(self):
        self.client.post("/query",
            json={"query": "What are the main risks Apple mentions?"},
            headers={"X-API-Key": API_KEY}
        )
    
    @task(1)
    def ask_out_of_scope(self):
        self.client.post("/query",
            json={"query": "Tell me about Google financials"},
            headers={"X-API-Key": API_KEY}
        )
    
    @task(1)
    def health_check(self):
        self.client.get("/health")