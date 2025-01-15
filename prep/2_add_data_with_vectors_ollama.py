from helpers import CollectionName, connect_to_weaviate
import h5py
import json
from tqdm import tqdm
import numpy as np


tenant_names = ["AcmeCo", "Globex", "Initech", "UmbrellaCorp", "WayneEnterprises"]


def import_from_hdf5(file_path: str):
    # Connect to Weaviate

    with connect_to_weaviate() as client:

        collection = client.collections.get(CollectionName.SUPPORTCHAT)

        if collection.config.get().multi_tenancy_config.enabled:
            use_multi_tenancy = True
        else:
            use_multi_tenancy = False

        # Open the HDF5 file
        with h5py.File(file_path, "r") as hf:
            # Get the total number of objects for the progress bar
            total_objects = len(hf.keys())

            # Use batch import for efficiency
            with client.batch.fixed_size(batch_size=200) as batch:
                for uuid in tqdm(
                    hf.keys(), total=total_objects, desc="Importing objects"
                ):
                    group = hf[uuid]

                    # Get the object properties
                    properties = json.loads(group["object"][()])

                    # Get the vector(s)
                    vectors = {}
                    for key in group.keys():
                        if key.startswith("vector_"):
                            vector_name = key.split("_", 1)[1]
                            vectors[vector_name] = np.asarray(group[key])

                    # If using multi-tenancy, assign a tenant (arbitrarily based on the company author length)
                    if use_multi_tenancy:
                        tenant_index = len(properties['company_author']) % 5
                        tenant = tenant_names[tenant_index]
                    else:
                        tenant = None

                    # Add the object to the batch
                    batch.add_object(
                        collection=CollectionName.SUPPORTCHAT,
                        uuid=uuid,
                        properties=properties,
                        vector={"text_with_metadata": vectors["text_with_metadata"]},
                        tenant=tenant,
                    )

    print(f"Import completed. {total_objects} objects imported.")
    if len(client.batch.failed_objects) > 0:
        print("*" * 80)
        print(f"***** Failed to add {len(client.batch.failed_objects)} objects *****")
        print("*" * 80)
        print(client.batch.failed_objects[:3])


if __name__ == "__main__":
    import_from_hdf5("data/twitter_customer_support_nomic.h5")
