from helpers import (
    CollectionName,
    connect_to_weaviate,
)

import json
from collections import Counter
from weaviate.classes.query import Filter
from weaviate.classes.config import Property, Configure, DataType, Tokenization

client = connect_to_weaviate()

client.collections.delete("TestCollection")

c = client.collections.create(
    name="TestCollection",
    properties=[
        Property(name="company", data_type=DataType.TEXT),
        Property(name="employee", data_type=DataType.TEXT)
    ],
    vectorizer_config=Configure.Vectorizer.none()
)

objs = [
    {"company": "Apple", "employee": "john"},
    {"company": "Apple", "employee": "jane"},
    {"company": "Weaviate", "employee": "john"},
]

c.data.insert_many(objs)

response = c.aggregate.over_all(
    total_count=True,
)

assert response.total_count == 3

response = c.aggregate.over_all(
    total_count=True,
    filters=Filter.by_property("company").equal("Apple")
)

assert response.total_count == 2

client.close()
