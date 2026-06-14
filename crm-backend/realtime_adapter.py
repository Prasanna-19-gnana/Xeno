from copy import deepcopy

from firestore_adapter import FirestoreCollectionAdapter, FirestoreCursor


class RealtimeCollectionAdapter(FirestoreCollectionAdapter):
    def __init__(self, realtime_db, name):
        self.realtime_db = realtime_db
        self.name = name
        self.collection_ref = realtime_db.reference(name)

    def insert_one(self, document):
        doc = deepcopy(document)
        doc_id = doc.get("_id")
        if not doc_id:
            doc_ref = self.collection_ref.push()
            doc["_id"] = doc_ref.key
            doc_ref.set(doc)
        else:
            self.collection_ref.child(str(doc_id)).set(doc)
        return {"inserted_id": doc["_id"]}

    def insert_many(self, documents):
        update_dict = {}
        inserted_ids = []
        for document in documents:
            doc = deepcopy(document)
            doc_id = doc.get("_id")
            if not doc_id:
                doc_ref = self.collection_ref.push()
                doc_id = doc_ref.key
                doc["_id"] = doc_id
            update_dict[str(doc_id)] = doc
            inserted_ids.append(doc_id)
        if update_dict:
            self.collection_ref.update(update_dict)
        return {"inserted_ids": inserted_ids}

    def delete_many(self, query=None):
        query = query or {}
        if not query:
            self.collection_ref.delete()
            return {"deleted_count": 0}
        docs = self._matching_documents(query)
        update_dict = {str(doc["_id"]): None for doc in docs}
        if update_dict:
            self.collection_ref.update(update_dict)
        return {"deleted_count": len(docs)}

    def update_one(self, query, update):
        doc = self.find_one(query)
        if not doc:
            return {"matched_count": 0, "modified_count": 0}

        updated = deepcopy(doc)

        for field, value in update.get("$set", {}).items():
            self._set_nested(updated, field, value)

        for field, value in update.get("$inc", {}).items():
            current = self._get_nested(updated, field) or 0
            self._set_nested(updated, field, current + value)

        for field, value in update.get("$addToSet", {}).items():
            current = self._get_nested(updated, field) or []
            if value not in current:
                current.append(value)
            self._set_nested(updated, field, current)

        self.collection_ref.child(str(updated["_id"])).set(updated)
        return {"matched_count": 1, "modified_count": 1}

    def find(self, query=None):
        return FirestoreCursor(self._matching_documents(query or {}))

    def _all_documents(self):
        raw_documents = self.collection_ref.get() or {}
        documents = []

        for doc_id, data in raw_documents.items():
            if isinstance(data, dict):
                document = deepcopy(data)
            else:
                document = {"value": data}
            document.setdefault("_id", doc_id)
            documents.append(document)

        return documents

    def _lookup(self, documents, spec):
        foreign_collection = RealtimeCollectionAdapter(self.realtime_db, spec["from"])
        foreign_documents = foreign_collection._all_documents()
        output = []

        for doc in documents:
            local_value = self._get_nested(doc, spec["localField"])
            matches = [
                foreign
                for foreign in foreign_documents
                if self._get_nested(foreign, spec["foreignField"]) == local_value
            ]
            new_doc = deepcopy(doc)
            new_doc[spec["as"]] = matches
            output.append(new_doc)

        return output


class RealtimeDatabaseAdapter:
    backend = "firebase-rtdb"

    def __init__(self, realtime_db):
        self.realtime_db = realtime_db

    def __getitem__(self, collection_name):
        return RealtimeCollectionAdapter(self.realtime_db, collection_name)

    def command(self, command_name):
        if command_name != "ping":
            raise ValueError(f"Unsupported Realtime Database command: {command_name}")
        self.realtime_db.reference("/").get()
        return {"ok": 1}
