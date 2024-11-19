from helpers import (
    CollectionName,
    connect_to_weaviate,
)

import json
from collections import Counter

client = connect_to_weaviate()

collection_name = CollectionName.SUPPORTCHAT
collection = client.collections.get(collection_name)

response = collection.query.fetch_objects(limit=2000)

companies = [c.properties["company_author"] for c in response.objects if c.properties["company_author"] != ""]

top_companies = Counter(companies).most_common(15)

with open("top_companies.json", "w") as f:
    json.dump(top_companies, f)

client.close()
