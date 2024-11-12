# File: ./3_query.py
from datetime import datetime
from helpers import CollectionName, connect_to_weaviate
from weaviate.classes.query import Filter, Metrics


# Connect to Weaviate
client = connect_to_weaviate()  # Uses `weaviate.connect_to_local` under the hood

chats = client.collections.get(CollectionName.SUPPORTCHAT)

for c in [1, 5]:
    response = chats.aggregate.over_all(
        return_metrics=Metrics("company_author").text(
            top_occurrences_count=True,
            top_occurrences_value=True,
            min_occurrences=c,
        ),
    )

    print(response.properties["company_author"])


query = "delivery problem"


response = chats.generate.hybrid(
    query=query,
    alpha=0.75,
    target_vector=["text_with_metadata"],
    filters=Filter.by_property("created_at").less_than(datetime(2017, 1, 1)),
    grouped_task="Summarise these support conversations. What topics are discussed?",
    limit=3,
)

print(response.generated)


client.close()
