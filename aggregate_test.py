from helpers import (
    CollectionName,
    connect_to_weaviate,
)

import json
from collections import Counter
from weaviate.classes.query import Filter

client = connect_to_weaviate()

collection_name = CollectionName.SUPPORTCHAT
collection = client.collections.get(collection_name)

response = collection.query.fetch_objects(limit=5)

for o in response.objects:
    if o.properties["company_author"] != "":
        company_author = o.properties["company_author"]
        break

print(o.properties["company_author"])

response = collection.aggregate.over_all(
    total_count=True,
    filters=Filter.by_property("company_author").equal(company_author)
)

print(response.total_count)

client.close()
