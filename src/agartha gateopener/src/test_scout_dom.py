
from src.agents.scout import ScoutAgent
from src.utils import safe_print

def test_scout():
    scout = ScoutAgent()
    
    # Test Fiverr (Python Bot)
    fiverr_url = "https://www.fiverr.com/search/gigs?query=python%20bot"
    safe_print(f"Testing Fiverr Capture on: {fiverr_url}")
    
    jobs = scout.fetch(fiverr_url, "fiverr")
    
    safe_print(f"Found {len(jobs)} jobs on Fiverr")
    for job in jobs[:3]:
        safe_print(f"- {job['title']} | {job['price']}")

    # Test Kwork/Qwork
    # qwork_url = "https://kwork.com/projects?c=11"
    # jobs = scout.fetch(qwork_url, "qwork")
    # safe_print(f"Found {len(jobs)} jobs on Qwork")

if __name__ == "__main__":
    test_scout()
