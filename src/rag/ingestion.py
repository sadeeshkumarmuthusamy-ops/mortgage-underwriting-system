import os
import requests
import tempfile
from urllib.parse import urlparse
import pypdf 
from langchain_community.document_loaders import PyPDFLoader

def validate_and_load_pdf(url: str):
    """
    Validates a URL, verifies the file exists, downloads it to a temp file,
    and loads it using PyPDFLoader.
    """
    try:
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            raise ValueError(f"Invalid URL format: {url}")
    except Exception:
        raise ValueError(f"Could not parse URL: {url}")

    print(f"Verifying access to: {url}...")
    try:
        response = requests.get(url, stream=True, timeout=10)
        
        if response.status_code != 200:
            raise ConnectionError(f"URL not accessible. Status Code: {response.status_code}")
            
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' not in content_type and not url.lower().endswith('.pdf'):
            raise ValueError(f"Target is not a PDF. Content-Type: {content_type}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Network error while connecting to URL: {e}")

    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_pdf.write(chunk)
            temp_file_path = temp_pdf.name

        print(f"Downloading successful. Loading from temp source: {temp_file_path}")
        
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        
        print(f"Successfully loaded {len(documents)} pages.")

        if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    print("Temporary file cleaned up.")

        return documents

    except Exception as e:
        raise RuntimeError(f"Failed to load PDF content: {e}")