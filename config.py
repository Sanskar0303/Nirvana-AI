import os
from dotenv import load_dotenv

# This line is crucial - it loads the .env file
load_dotenv()

# These lines read the keys from the environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")
OPENWEATHER_API_KEY="1e6891f2519c1277cda22273c659f026"
TAVILY_API_KEY = "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"
