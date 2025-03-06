# File: ./0_reset_cluster.py
# Run this to delete the workshop data, if you have any, and start from scratch
from helpers import CollectionName, connect_to_weaviate


# Connect to Weaviate
client = connect_to_weaviate()  # Uses `weaviate.connect_to_local` under the hood

# Delete existing collection if it exists
client.collections.delete(CollectionName.SUPPORTCHAT)

client.close()
