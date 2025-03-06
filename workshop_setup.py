import os
import click
import requests
import shutil
from pathlib import Path
from tqdm import tqdm


@click.command()
@click.option("--provider", default="ollama", help="Which model provider to use.")
@click.option("--dataset-size", default="50000", help="Size of the dataset to use.")
@click.option("--use-cache", is_flag=True, default=True, help="Use cached files if available.")
def setup(provider, dataset_size, use_cache):
    """Set up collection with the specified provider configuration."""
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

    # Download dataset
    download_dataset(provider, dataset_size, use_cache)

    # Update configurations in both files
    update_configurations(provider)

    # Delete existing collection if it exists
    os.system("python 0_reset_cluster.py")


def download_dataset(provider, dataset_size, use_cache):
    """Download the dataset for the specified provider."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    url_suffixes = {
        "ollama": "nomic",
        "openai": "openai-text-embedding-3-small",
        "cohere": "cohere-embed-multilingual-light-v3.0"
    }

    provider_suffixes = {
        "ollama": "nomic",
        "openai": "openai",
        "cohere": "cohere"
    }

    dl_filename = f"twitter_customer_support_{provider_suffixes[provider]}_{dataset_size}.h5"
    out_filename = "twitter_customer_support.h5"

    if (data_dir / dl_filename).exists() and use_cache:
        print(f"Using cached file {dl_filename}...")
    else:
        if use_cache:
            print(f"No cached file {dl_filename} found.")
        url = f"https://weaviate-workshops.s3.eu-west-2.amazonaws.com/odsc-europe-2024/twitter_customer_support_weaviate_export_{dataset_size}_{url_suffixes[provider]}.h5"
        download_file(url, data_dir / dl_filename)

    # Copy to standardized filename
    if dl_filename != out_filename:
        shutil.copy(data_dir / dl_filename, data_dir / out_filename)


def update_configurations(selected_provider):
    """Update configurations in both files for the selected provider."""
    # Update the collection creation script
    toggle_provider_config("1_create_collection.py", selected_provider)

    # Update the import script's file path
    update_import_file_path("2_add_data_with_vectors.py")


def toggle_provider_config(file_path, selected_provider):
    """Toggle provider configurations in the collection creation file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    modified_lines = []
    in_provider_section = False
    current_provider = None

    for line in lines:
        # Detect provider section starts
        if "# Ollama" in line or "# OpenAI" in line or "# Cohere" in line:
            current_provider = line.strip('# \n')
            in_provider_section = True

        # Handle the line based on context
        if in_provider_section:
            if current_provider.lower() == selected_provider:
                # Selected provider: ensure lines are uncommented
                if line.strip().startswith('# ') and not any(marker in line for marker in ['# Ollama', '# OpenAI', '# Cohere', '# END_Provider']):
                    line = "    " + line[6:]  # Remove comment
                modified_lines.append(line)
            else:
                # Other providers: ensure lines are commented
                if not line.strip().startswith('#'):
                    line = '    # ' + line[4:]
                modified_lines.append(line)

            # Check for end of provider section
            if "# END_Provider" in line:
                in_provider_section = False
                current_provider = None
        else:
            # Outside provider sections: keep line as is
            modified_lines.append(line)

    # Write the modified content back to the file
    with open(file_path, 'w') as f:
        f.writelines(modified_lines)

    print(f"Updated {file_path} to use {selected_provider} configuration")


def update_import_file_path(file_path):
    """Update the import file path in the data import script."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    modified_lines = []
    for line in lines:
        if 'import_from_hdf5("data/twitter_customer_support' in line:
            # Use the standardized filename
            new_line = '    import_from_hdf5("data/twitter_customer_support.h5")\n'
            modified_lines.append(new_line)
        else:
            modified_lines.append(line)

    # Write the modified content back to the file
    with open(file_path, 'w') as f:
        f.writelines(modified_lines)

    print(f"Updated {file_path} with standardized file path")


def download_file(url, filepath):
    """Download a file with progress bar."""
    temp_filepath = filepath.with_suffix(".part")

    print(f"Downloading {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get("content-length", 0))

    with open(temp_filepath, "wb") as file, tqdm(
        desc=filepath.name,
        total=total_size,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)

    temp_filepath.rename(filepath)
    print(f"File downloaded to {filepath}")


if __name__ == "__main__":
    setup()
