# File: ./1_create_collection.py
from weaviate.classes.config import Property, DataType, Configure
from helpers import CollectionName, connect_to_weaviate


# Connect to Weaviate
client = connect_to_weaviate()  # Uses `weaviate.connect_to_local` under the hood

# Delete existing collection if it exists
client.collections.delete(CollectionName.SUPPORTCHAT)

# Try different vector index configurations and see how they affect the speed, memory usage & recall
default_vindex_config = Configure.VectorIndex.hnsw(
    # quantizer=Configure.VectorIndex.Quantizer.bq()
    # quantizer=Configure.VectorIndex.Quantizer.sq(training_limit=25000)
    # quantizer=Configure.VectorIndex.Quantizer.pq(training_limit=25000)
)

# Create a new collection with specified properties and vectorizer configuration
chunks = client.collections.create(
    name=CollectionName.SUPPORTCHAT,
    properties=[
        Property(name="text", data_type=DataType.TEXT),
        Property(name="dialogue_id", data_type=DataType.INT),
        Property(name="company_author", data_type=DataType.TEXT),
        Property(name="created_at", data_type=DataType.DATE),
    ],
    # ================================================================================
    # Set up the collection to use OpenAI
    # ================================================================================
    vectorizer_config=[
        Configure.NamedVectors.text2vec_openai(
            name="text",
            source_properties=["text"],
            vector_index_config=default_vindex_config,
            model="text-embedding-3-small",
        ),
        Configure.NamedVectors.text2vec_openai(
            name="text_with_metadata",
            source_properties=["text", "company_author"],
            vector_index_config=default_vindex_config,
            model="text-embedding-3-small",
        ),
    ],
    generative_config=Configure.Generative.openai(model="gpt-3.5-turbo-16k"),
    # ================================================================================
    # END: OpenAI configuration
    # ================================================================================
    #
    # ================================================================================
    # Uncomment this section to enable multi-tenancy
    # ================================================================================
    multi_tenancy_config=Configure.multi_tenancy(
        enabled=True,
        auto_tenant_creation=True,
    ),
)

assert client.collections.exists(CollectionName.SUPPORTCHAT)

client.close()
