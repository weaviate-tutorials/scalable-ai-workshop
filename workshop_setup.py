import os
import click
import requests
from pathlib import Path
from tqdm import tqdm
import shutil


@click.command()
@click.option("--provider", default="ollama", help="Which model provider to use.")
@click.option("--dataset-size", default="50000", help="Size of the dataset to use.")
@click.option("--use-cache", is_flag=True, help="Use cached files if available.")
def download(provider, dataset_size, use_cache):
    """Download prerequisite files & confirm required aspects."""
    available_dataset_sizes = ["10000", "50000", "100000", "200000"]
    available_providers = ["ollama", "openai", "cohere"]

    if dataset_size not in available_dataset_sizes:
        print(f"Sorry, the dataset size '{dataset_size}' is not available.")
        print(f"Please choose from {available_dataset_sizes}")
        return

    if provider not in available_providers:
        print(f"Sorry, the provider '{provider}' is not available.")
        print(f"Please choose from {available_providers}")
        return

    # Create `data` directory if it does not exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    if provider == "ollama":
        # Download file
        out_filename = f"twitter_customer_support_nomic.h5"

        if (data_dir / out_filename).exists() and use_cache:
            print(f"Using cached file {out_filename}...")
        else:
            if use_cache:
                print(f"No cached file {out_filename} found.")
            url = f"https://weaviate-workshops.s3.eu-west-2.amazonaws.com/odsc-europe-2024/twitter_customer_support_weaviate_export_{dataset_size}_nomic.h5"
            download_file(url, data_dir / out_filename)

        # Run Ollama commands
        print("Running 'ollama pull nomic-embed-text'...")
        os.system("ollama pull nomic-embed-text")

        print("Running 'ollama pull gemma2:2b'...")
        os.system("ollama pull gemma2:2b")

    elif provider == "openai":
        # Download file
        out_filename = f"twitter_customer_support_openai.h5"

        if (data_dir / out_filename).exists() and use_cache:
            print(f"Using cached file {out_filename}...")
        else:
            if use_cache:
                print(f"No cached file {out_filename} found.")
            url = f"https://weaviate-workshops.s3.eu-west-2.amazonaws.com/odsc-europe-2024/twitter_customer_support_weaviate_export_{dataset_size}_openai-text-embedding-3-small.h5"
            download_file(url, data_dir / out_filename)

        # Check for OPENAI_API_KEY
        if not os.environ.get("OPENAI_API_KEY"):
            print("Warning: OPENAI_API_KEY is not set in the environment variables.")
        else:
            print("OPENAI_API_KEY is set.")

    elif provider == "cohere":
        # Download file
        out_filename = f"twitter_customer_support_cohere.h5"

        if (data_dir / out_filename).exists() and use_cache:
            print(f"Using cached file {out_filename}...")
        else:
            if use_cache:
                print(f"No cached file {out_filename} found.")
            url = f"https://weaviate-workshops.s3.eu-west-2.amazonaws.com/odsc-europe-2024/twitter_customer_support_weaviate_export_{dataset_size}_cohere-embed-multilingual-light-v3.0.h5"
            download_file(url, data_dir / out_filename)

        # Check for COHERE_API_KEY
        if not os.environ.get("COHERE_API_KEY"):
            print("Warning: COHERE_API_KEY is not set in the environment variables.")
        else:
            print("COHERE_API_KEY is set.")

    else:
        print(f"Sorry, the provider value '{provider}' is not supported.")

    # Copy appropriate configuration file
    for src_config, dest_config in [
        (f"prep/1_create_collection_{provider}.py", "1_create_collection.py"),
        (f"prep/2_add_data_with_vectors_{provider}.py", "2_add_data_with_vectors.py"),
    ]:
        shutil.copy(src_config, dest_config)
        print(f"Copied {src_config} to {dest_config}")


def download_file(url, filepath):
    print(f"Downloading {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))

    with open(filepath, "wb") as file, tqdm(
        desc=filepath.name,
        total=total_size,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)

    print(f"File downloaded to {filepath}")


if __name__ == "__main__":
    download()
