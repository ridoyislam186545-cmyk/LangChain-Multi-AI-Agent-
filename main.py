from dotenv import load_dotenv
load_dotenv()
from src.pipelines.pipeline import run_research_pipeline
topic = "The impact of  AI on the Job Market in 2026 "
run_research_pipeline(topic)