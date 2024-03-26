class HashTable:
    def __init__(self, initial_capacity=40): # Creates the hash map with a capacity of 40
        self.table = []
        for i in range(initial_capacity):
            self.table.append([])

    def insert(self, key, item): # converts the package ID into a hash key value and inputs data
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        for kv in bucket_list:
            if kv[0] == key:
                kv[1] = item
                return True

        key_value = [key, item]
        bucket_list.append(key_value)
        return True

    def remove(self, key, item): # Removes the bucket data using the package ID as key value
        bucket = hash(item) % len(self.table)
        bucket_list = self.table[bucket]

        for kv in bucket_list:
            if kv[0] == key:
                bucket_list.remove([kv[0], kv[1]])

    def search(self, key): # Retrieves package data using the package ID as a key value
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        for kv in bucket_list:
            if kv[0] == key:
                return kv[1]
        return None

