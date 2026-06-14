import re
from copy import deepcopy


def _sort_key(value):
    if value is None:
        return (0, "")
    if isinstance(value, (int, float)):
        return (1, value)
    return (2, str(value))


class FirestoreCursor:
    def __init__(self, documents):
        self.documents = list(documents)

    def sort(self, field, direction=1):
        reverse = direction == -1
        self.documents.sort(key=lambda doc: _sort_key(doc.get(field)), reverse=reverse)
        return self

    def skip(self, count):
        self.documents = self.documents[count:]
        return self

    def limit(self, count):
        self.documents = self.documents[:count]
        return self

    def __iter__(self):
        return iter(self.documents)

    def __len__(self):
        return len(self.documents)


class FirestoreCollectionAdapter:
    def __init__(self, firestore_client, name):
        self.firestore_client = firestore_client
        self.name = name
        self.collection_ref = firestore_client.collection(name)

    def create_index(self, *_args, **_kwargs):
        return None

    def insert_one(self, document):
        doc = deepcopy(document)
        doc_id = doc.get("_id")
        if not doc_id:
            doc_ref = self.collection_ref.document()
            doc["_id"] = doc_ref.id
            doc_ref.set(doc)
        else:
            self.collection_ref.document(str(doc_id)).set(doc)
        return {"inserted_id": doc["_id"]}

    def insert_many(self, documents):
        inserted_ids = []
        batch = self.firestore_client.batch()
        batch_size = 0

        for document in documents:
            doc = deepcopy(document)
            doc_id = doc.get("_id")
            doc_ref = self.collection_ref.document(str(doc_id)) if doc_id else self.collection_ref.document()
            if not doc_id:
                doc["_id"] = doc_ref.id
            batch.set(doc_ref, doc)
            inserted_ids.append(doc["_id"])
            batch_size += 1

            if batch_size >= 450:
                batch.commit()
                batch = self.firestore_client.batch()
                batch_size = 0

        if batch_size:
            batch.commit()

        return {"inserted_ids": inserted_ids}

    def find_one(self, query=None):
        docs = self._matching_documents(query or {})
        return docs[0] if docs else None

    def find(self, query=None):
        return FirestoreCursor(self._matching_documents(query or {}))

    def count_documents(self, query=None):
        return len(self._matching_documents(query or {}))

    def delete_many(self, query=None):
        docs = self._matching_documents(query or {})
        batch = self.firestore_client.batch()
        deleted = 0

        for doc in docs:
            batch.delete(self.collection_ref.document(str(doc["_id"])))
            deleted += 1

            if deleted % 450 == 0:
                batch.commit()
                batch = self.firestore_client.batch()

        if deleted and deleted % 450 != 0:
            batch.commit()

        return {"deleted_count": deleted}

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

        self.collection_ref.document(str(updated["_id"])).set(updated)
        return {"matched_count": 1, "modified_count": 1}

    def distinct(self, field, query=None):
        values = []
        seen = set()
        for doc in self._matching_documents(query or {}):
            value = self._get_nested(doc, field)
            if isinstance(value, list):
                candidates = value
            else:
                candidates = [value]

            for candidate in candidates:
                if candidate is not None and candidate not in seen:
                    seen.add(candidate)
                    values.append(candidate)

        return values

    def aggregate(self, pipeline):
        documents = self._all_documents()

        for stage in pipeline:
            if "$match" in stage:
                documents = [doc for doc in documents if self._matches_query(doc, stage["$match"])]
            elif "$lookup" in stage:
                documents = self._lookup(documents, stage["$lookup"])
            elif "$unwind" in stage:
                documents = self._unwind(documents, stage["$unwind"])
            elif "$project" in stage:
                documents = self._project(documents, stage["$project"])
            elif "$group" in stage:
                documents = self._group(documents, stage["$group"])
            elif "$sort" in stage:
                for field, direction in reversed(stage["$sort"].items()):
                    documents.sort(
                        key=lambda doc: _sort_key(doc.get(field)),
                        reverse=direction == -1
                    )
            elif "$skip" in stage:
                documents = documents[stage["$skip"]:]
            elif "$limit" in stage:
                documents = documents[:stage["$limit"]]

        return documents

    def _all_documents(self):
        documents = []
        for snapshot in self.collection_ref.stream():
            data = snapshot.to_dict() or {}
            data.setdefault("_id", snapshot.id)
            documents.append(data)
        return documents

    def _matching_documents(self, query):
        return [doc for doc in self._all_documents() if self._matches_query(doc, query)]

    def _matches_query(self, document, query):
        for field, condition in query.items():
            if field == "$or":
                if not any(self._matches_query(document, option) for option in condition):
                    return False
                continue

            value = self._get_nested(document, field)
            if isinstance(condition, dict):
                regex = condition.get("$regex")
                if regex is not None:
                    flags = re.IGNORECASE if "i" in condition.get("$options", "") else 0
                    if value is None or not re.search(regex, str(value), flags):
                        return False

                for operator, expected in condition.items():
                    if operator in ("$regex", "$options"):
                        continue
                    if operator == "$gt" and not (value is not None and value > expected):
                        return False
                    if operator == "$gte" and not (value is not None and value >= expected):
                        return False
                    if operator == "$lt" and not (value is not None and value < expected):
                        return False
                    if operator == "$lte" and not (value is not None and value <= expected):
                        return False
                    if operator == "$ne" and value == expected:
                        return False
                    if operator == "$in" and value not in expected:
                        return False
            elif value != condition:
                return False

        return True

    def _lookup(self, documents, spec):
        foreign_collection = FirestoreCollectionAdapter(self.firestore_client, spec["from"])
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

    def _unwind(self, documents, spec):
        if isinstance(spec, str):
            path = spec.lstrip("$")
            preserve_empty = False
        else:
            path = spec["path"].lstrip("$")
            preserve_empty = spec.get("preserveNullAndEmptyArrays", False)

        output = []
        for doc in documents:
            value = self._get_nested(doc, path)
            if isinstance(value, list) and value:
                for item in value:
                    new_doc = deepcopy(doc)
                    self._set_nested(new_doc, path, item)
                    output.append(new_doc)
            elif preserve_empty:
                output.append(doc)

        return output

    def _project(self, documents, projection):
        output = []

        for doc in documents:
            projected = {}
            for field, expression in projection.items():
                if expression == 1:
                    projected[field] = self._get_nested(doc, field)
                elif isinstance(expression, dict) and "$ifNull" in expression:
                    for candidate in expression["$ifNull"]:
                        if isinstance(candidate, str) and candidate.startswith("$"):
                            value = self._get_nested(doc, candidate[1:])
                        else:
                            value = candidate
                        if value is not None:
                            projected[field] = value
                            break
                elif isinstance(expression, str) and expression.startswith("$"):
                    projected[field] = self._get_nested(doc, expression[1:])
                else:
                    projected[field] = expression
            output.append(projected)

        return output

    def _group(self, documents, spec):
        grouped = {}
        group_expr = spec.get("_id")

        for doc in documents:
            if isinstance(group_expr, str) and group_expr.startswith("$"):
                group_key = self._get_nested(doc, group_expr[1:])
            else:
                group_key = group_expr

            grouped.setdefault(group_key, {"_id": group_key})
            target = grouped[group_key]

            for field, expression in spec.items():
                if field == "_id":
                    continue
                if "$sum" in expression:
                    sum_expr = expression["$sum"]
                    if isinstance(sum_expr, str) and sum_expr.startswith("$"):
                        value = self._get_nested(doc, sum_expr[1:]) or 0
                    else:
                        value = sum_expr
                    target[field] = target.get(field, 0) + value

        return list(grouped.values())

    def _get_nested(self, document, dotted_field):
        value = document
        for part in dotted_field.split("."):
            if not isinstance(value, dict):
                return None
            value = value.get(part)
        return value

    def _set_nested(self, document, dotted_field, value):
        target = document
        parts = dotted_field.split(".")
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = value


class FirestoreDatabaseAdapter:
    backend = "firebase"

    def __init__(self, firestore_client):
        self.firestore_client = firestore_client

    def __getitem__(self, collection_name):
        return FirestoreCollectionAdapter(self.firestore_client, collection_name)

    def command(self, command_name):
        if command_name != "ping":
            raise ValueError(f"Unsupported Firestore command: {command_name}")
        return {"ok": 1}
