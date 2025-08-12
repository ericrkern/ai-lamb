import os
import git
import json
import argparse
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader

# Load Env Variables
from dotenv import load_dotenv

load_dotenv()

# For BedRock
from langchain_aws import BedrockEmbeddings

def process_repository(repo_url, repo_name):
    """Process a single repository"""
    repo_path = f"./repositories/{repo_name}"
    
    # Create repositories directory if it doesn't exist
    os.makedirs("./repositories", exist_ok=True)
    
    if os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git")):
        print(f"Directory {repo_path} already contains a git repository.")
    else:
        try:
            repo = git.Repo.clone_from(repo_url, repo_path)
            print(f"Repository cloned into: {repo_path}")
        except Exception as e:
            print(f"An error occurred while cloning the repository {repo_url}: {e}")
            return False
    
    try:
        # Initialize embeddings
        embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")
        
        # Load documents
        loader = DirectoryLoader(repo_path, glob="**/*.*", silent_errors=True)
        documents = loader.load()
        
        if not documents:
            print(f"No documents found in {repo_path}")
            return False
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=8000, chunk_overlap=100)
        texts = text_splitter.split_documents(documents)
        
        # Create vector database
        db = FAISS.from_documents(texts, embeddings)
        
        # Create vector_db directory if it doesn't exist (one level up from repositories)
        os.makedirs("../vector_db", exist_ok=True)
        
        # Save vector database
        db_path = f"../vector_db/{repo_name}.faiss"
        db.save_local(db_path)
        print(f"Vector database saved to: {db_path}")
        
        return True
        
    except Exception as e:
        print(f"An error occurred while processing {repo_name}: {e}")
        return False

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Process repositories from a JSON file and create vector databases')
    parser.add_argument('json_file', help='Path to the JSON file containing repository information')
    parser.add_argument('--output-dir', default='../../vector_db', help='Output directory for vector databases (default: ./vector_db)')
    
    args = parser.parse_args()
    
    # Load repositories from JSON file
    try:
        with open(args.json_file, 'r') as f:
            repos_data = json.load(f)
    except FileNotFoundError:
        print(f"JSON file {args.json_file} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error parsing JSON file {args.json_file}")
        return
    
    # Handle both formats: direct array or wrapped in "repositories" key
    if isinstance(repos_data, dict) and "repositories" in repos_data:
        repos_data = repos_data["repositories"]
    
    print(f"Loading repositories from: {args.json_file}")
    print(f"Output directory: {args.output_dir}")
    
    # Process each repository
    successful = 0
    failed = 0
    
    for repo_info in repos_data:
        if isinstance(repo_info, dict):
            repo_url = repo_info.get('url')
            repo_name = repo_info.get('name')
        elif isinstance(repo_info, str):
            # If it's just a URL string, extract name from URL
            repo_url = repo_info
            repo_name = repo_url.split('/')[-1].replace('.git', '')
        else:
            print(f"Invalid repository format: {repo_info}")
            failed += 1
            continue
        
        if not repo_url:
            print(f"No URL found for repository: {repo_info}")
            failed += 1
            continue
        
        if not repo_name:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
        
        print(f"\nProcessing repository: {repo_name}")
        print(f"URL: {repo_url}")
        
        success = process_repository(repo_url, repo_name)
        if success:
            print(f"Successfully processed {repo_name}")
            successful += 1
        else:
            print(f"Failed to process {repo_name}")
            failed += 1
    
    print(f"\n=== Summary ===")
    print(f"Successfully processed: {successful}")
    print(f"Failed: {failed}")
    print(f"Total: {successful + failed}")

if __name__ == "__main__":
    main()