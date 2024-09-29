import logging
from datetime import datetime, timedelta

import requests

from strava_client import swagger_client
from strava_client.swagger_client.rest import ApiException

CLIENT_ID = 100568
CLIENT_SECRET = "acf561a680338fe683dd191527421f30b0f94e36"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_ACTIVITIES_URL = "https://www.strava.com/api/v3/activities"


class StravaAPI:

    def __init__(self, refresh_token: str, start_date: float = None):
        self.refresh_token = refresh_token
        self.api_instance = None
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).timestamp()
        self.start_date = start_date

    def get_api_client(self):
        if not self.api_instance:
            access_token = self.get_access_token()
            if not access_token:
                logging.error(f"No access token")
                raise

        # Make the API request to retrieve activities and process the response.
            try:
                configuration = swagger_client.Configuration()
                configuration.access_token = access_token
                api_instance = swagger_client.ActivitiesApi(swagger_client.ApiClient(configuration))
            except requests.RequestException as e:
                logging.error(f"Error creating the Api client")
                raise
            self.api_instance = api_instance
        return self.api_instance

    def get_access_token(self) -> str:
        logging.info("Start refresh_token")
        try:
            response = requests.post(
                STRAVA_TOKEN_URL,
                params={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "refresh_token": self.refresh_token,
                    "grant_type": "refresh_token"
                }
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error refreshing access token: {e}")
            return None

        try:
            response_json = response.json()
        except requests.JSONDecodeError as e:
            logging.error(f"Error decoding JSON response: {e}")
            return None

        access_token = response_json.get("access_token")
        if not access_token:
            logging.error("Access token not found in the response")
            return None

        return access_token

    def get_activities(self) -> list:

        api_instance = self.get_api_client()

        try:
            activities_json = self._get_activities_paginated(api_instance)

        except requests.JSONDecodeError as e:
            logging.error(f"Error decoding JSON response for activities: {e}")
            return []

        return activities_json

    def _get_activities_paginated(self, api_instance, per_page=200):
        all_activities = []
        page = 1
        while True:
            try:
                # List Athlete Activities
                api_response = api_instance.get_logged_in_athlete_activities(
                    page=page, per_page=per_page, after=self.start_date
                )
                if not api_response:  # If there are no more activities, break the loop
                    break
                all_activities.extend(api_response)
                page += 1
            except ApiException as e:
                print("Exception when calling ActivitiesApi->get_logged_in_athlete_activities: %s\n" % e)
                break
        return all_activities

    def create_activity(
        self, name, activity_type, start_date_local, elapsed_time, description=None,
        distance=None
    ):
        """
        Create a single activity on Strava.
        """
        api_instance = self.get_api_client()

        try:
            api_response = api_instance.create_activity(
                name=name,
                type=activity_type,
                start_date_local=start_date_local,
                elapsed_time=elapsed_time,
                description=description,
                distance=distance,
                sport_type='Run',
                trainer=0,
                commute=0
            )
            return api_response
        except Exception as e:
            print(f"Exception when calling ActivitiesApi->create_activity: {e}\n")
            raise

    def create_multiple_activities(self, activities_data):
        """
        Create multiple activities on Strava.
        activities_data: List of dictionaries with keys: name, activity_type, start_date_local
        , elapsed_time, description, distance
        """
        try:
            for idx, activity_data in enumerate(activities_data):
                self.create_activity(
                    name=f"{activity_data['name']}",
                    activity_type=activity_data['activity_type'],
                    start_date_local=activity_data['start_date_local'],
                    elapsed_time=activity_data['elapsed_time'],
                    description=activity_data.get('description'),
                    distance=activity_data.get('distance')
                )
                logging.info("Created Activity", {"idx": idx})
        except Exception:
            logging.error("Error creating activities")
            return False
        return True


if __name__ == "__main__":
    # strava_api = StravaAPI(refresh_token="ae9c3270df56ba4e4200595530291d0731ca475e")
    # act = strava_api.get_activities()
    # print(act)

    base_start_date = datetime.now()
    activities_data = []
    for idx in range(600,1000):
        start_date = base_start_date + timedelta(minutes=idx)  # Slightly different start dates
        activities_data.append({
            "name": f"Test Activity {idx}",
            "activity_type": "Run",
            "start_date_local": start_date.isoformat() + "Z",  # Convert to ISO format
            "elapsed_time": 3600,  # 1 hour in seconds
            "description": f"Test activity number {idx}",
            "distance": 10000  # 10 km in meters
        })
    strava_api = StravaAPI(refresh_token="35e7e8164708423509aa27efa02d5fed82b106fe")
    created_activities = strava_api.create_multiple_activities(activities_data)


