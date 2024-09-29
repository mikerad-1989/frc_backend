from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore


class DBConsts:
    EVENTS_TABLE = 'events'
    STATS_TABLE = 'stats'
    USERS_TABLE = 'users'


class FirestoreDatabase:
    def __init__(self):
        base_path = Path(__file__).resolve().parent
        self.cred = credentials.Certificate(
            f"{base_path}/foundersrc-firebase-adminsdk-b4b78-7710c5e417.json"
        )
        self.db = None

    def get_db_client(self):
        if not self.db:
            try:
                firebase_admin.initialize_app(self.cred)
            except ValueError:
                print(f"Already initialized the Firebase app")
            db = firestore.client()
            db._database = 'dbfrc'
            self.db = db
        return self.db

    def get_collection_with_filters(self, collection_name, filters=None):
        """
        Retrieve documents from a specific collection with optional filters.

        :param collection_name: Name of the collection to retrieve.
        :param filters: A list of tuples, each containing field, operator, and value for filtering.
        :return: List of documents matching the filters.
        """
        try:
            db = self.get_db_client()
            collection_ref = db.collection(collection_name)
            if filters:
                for filter in filters:
                    field, op, value = filter
                    collection_ref = collection_ref.where(field, op, value)
            docs = collection_ref.stream()
            docs_json = []
            for doc in docs:
                doc_dict = doc.to_dict()
                doc_dict['id'] = doc.id
                docs_json.append(doc_dict)
            return docs_json
        except Exception as e:
            print(f"An error occurred while retrieving documents: {e}")
            return []

    def get_document_by_field(self, collection_name, field_name, field_value):
        """
        Retrieve a document from a specific collection by a field name and value.

        :param collection_name: Name of the collection to retrieve from.
        :param field_name: The field name to filter by.
        :param field_value: The value of the field to filter by.
        :return: The first matching document or None if no match is found.
        """
        try:
            db = self.get_db_client()
            collection_ref = db.collection(collection_name)
            query = collection_ref.where(field_name, '==', field_value).limit(1)
            results = query.stream()

            return list(results)[0].to_dict() if results else None
        except Exception as e:
            print(f"An error occurred while retrieving the document: {e}")
        return None

    def update_document(self, collection_name, document_id, data):
        """
        Update an existing document or create it if it does not exist.

        :param collection_name: Name of the collection where the document will be updated.
        :param document_id: The ID of the document to update.
        :param data: A dictionary representing the fields to update in the document.
        :return: None
        """
        try:
            db = self.get_db_client()
            document_ref = db.collection(collection_name).document(document_id)
            document_ref.set(data, merge=True)
        except Exception as e:
            print(f"An error occurred while updating the document: {e}")

    def insert_entity(self, collection_name, entity_data):
        """
        Insert a new document into a specified collection.

        :param collection_name: Name of the collection where the document will be inserted.
        :param entity_data: A dictionary representing the document to be inserted.
        :return: The ID of the inserted document.
        """
        try:
            db = self.get_db_client()
            doc_ref = db.collection(collection_name).add(entity_data)
            return doc_ref[1].id  # doc_ref is a tuple (DocumentReference, WriteResult)
        except Exception as e:
            print(f"An error occurred while inserting the document: {e}")
            return None

    def insert_calendar_events(self, calendar_events):
        """
        Adds or updates entities in a Firestore collection based on calendar_name and start_time.

        """
        db = self.get_db_client()
        for entity in calendar_events:
            calendar_name = entity.get("calendar_name")
            start_time = entity.get("start_time")

            # Query to find existing document
            query = db.collection(DBConsts.EVENTS_TABLE).where(
                "calendar_name", "==", calendar_name
            ).where("start_time", "==", start_time)
            results = query.get()
            if results:
                # If document exists, update it
                doc_id = results[0].id
                db.collection(DBConsts.EVENTS_TABLE).document(doc_id).update(entity)
                print(f"Updated entity with calendar_name: {calendar_name} and start_time: {start_time}")
            else:
                # If document doesn't exist, add a new one
                db.collection(DBConsts.EVENTS_TABLE).add(entity)
                print(f"Added new entity with calendar_name: {calendar_name} and start_time: {start_time}")

    def insert_stats(self, stats: dict):
        """
        Adds or updates entities in a Firestore collection based on user_id.

        """
        db = self.get_db_client()
        user_id = stats.get("user_id")

        # Query to find existing document
        query = db.collection(DBConsts.STATS_TABLE).where(
            "user_id", "==", user_id
        )
        results = query.get()
        if results:
            # If document exists, update it
            doc_id = results[0].id
            db.collection(DBConsts.STATS_TABLE).document(doc_id).update(stats)
            print(f"Updated entity with user_id: {user_id}")
        else:
            # If document doesn't exist, add a new one
            db.collection(DBConsts.STATS_TABLE).add(stats)
            print(f"Added new entity with stats: {stats}")


# Example usage:
if __name__ == "__main__":
    db = FirestoreDatabase()

    # Example to retrieve documents with filters
    filters = [('age', '>=', 21), ('active', '==', True)]
    documents = db.get_collection_with_filters('users', filters)
    for doc in documents:
        print(doc)

    # Example to insert a new document
    new_user = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'age': 30,
        'active': True
    }
    new_doc_id = db.insert_entity('users', new_user)
    print(f"Inserted new document with ID: {new_doc_id}")
