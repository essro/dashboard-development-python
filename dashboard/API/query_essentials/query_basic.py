"""
file: query_basic.py
author: Aarron Stewart
created: 2/5/2017

"""

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import os.path


def get_client_credentials():
    """

    :return: Returns the full file path for the Google API Service Email Credentials
    """
    creds_filename = "d3cubed-fe243687c378.p12"
    creds_fullpath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'credentials', creds_filename))
    return creds_fullpath


def get_svc_account():
    """

    :return: Returns the Google API Service Email
    """
    return "api-930@d3cubed-157122.iam.gserviceaccount.com"


def get_service(api_name, 
                api_version, 
                scope, 
                key_file_location,
                service_account_email):
    """
    This function was created by Google for Hello Analyctics API tutorial
    Get a service that communicates to a Google API.

    Args:
      api_name: The name of the api to connect to.
      api_version: The api version to connect to.
      scope: A list auth scopes to authorize for the application.
      key_file_location: The path to a valid service account p12 key file.
      service_account_email: The service account email address.

    Returns:
      A service that is connected to the specified API.
    """

    # setup the credentials for the Google API
    credentials = ServiceAccountCredentials.from_p12_keyfile(
      service_account_email, key_file_location, scopes=scope)

    http = credentials.authorize(httplib2.Http())

    # Build the service object.
    service = build(api_name, api_version, http=http)

    return service


def get_account_id(service):
    """

    :param service: The service that provides credentials for Google
    :return: List of JSON formated elements with the account information
    """

    # initialize variables
    list_accounts = []

    # perform API request for account information
    account = service.management().accounts().list().execute()

    # print(account.get('items'))
    if account.get('items'):

        # loop across the results and append the account information to the list
        for index in range(0, account.get('totalResults')):

            # append account information to the list
            list_accounts.append(account.get('items')[index])

        # print(list_accounts)
        return list_accounts

    return None


def get_profile_id(service, account):
    """

    :param service: The service that provides credential for Google
    :param account: A JSON formatted element with all necessary information
    :return: A 2D list the first array is the properties and the seccond array is the profile ids.
    """
    # Use the Analytics service object to get the first profile id.
    prop = []

    # get the account ID that you wish to use
    account_id = account.get('id')

    # Get a list of all the properties for the first account.
    properties = service.management().webproperties().list(
        accountId=account_id).execute()

    # test to see if there is an element to extract
    if properties.get( "items"):

        # Get the first property id.
        for index in range(0, properties.get("totalResults")):

            # get the current property id number
            property = properties.get('items')[index].get('id')

            # Get a list of all views (profiles) for the first property.
            profiles = service.management().profiles().list(
                    accountId=account_id,
                    webPropertyId=property).execute()

            # if there is an element to extract get the list of Profile IDs
            if profiles.get('items'):

                # append the profile id to the list
                prop.append(get_profile_id_list(profiles))

        # return the correct information to the calling method
        return prop

    return None


def get_profile_id_list(profile):
    """

    :param profile: property information that includes the profile IDs
    :return: Returns a list of all profile IDs for a property
    """
    # initialize variables
    profileID = []

    # loop across the JSON getting the profile ID from the current element
    for index in range(0, profile.get('totalResults')):

        # return the first view (profile) id.
        profileID.append( profile.get('items')[index].get('id'))

    # return the list to the calling method
    return profileID


def get_results(context):
    """

    :param context: A dictionary that contains all information required for the dashboard element.
    :return: A JSON formatted data element with all required information from Google Analytics.
    """

    # get service information about the account
    service = get_service(context.get("api_name"),
                           context.get("api_version"),
                           context.get("scope"),
                           context.get("key_file_location"),
                           context.get("svc_account_email")
                           )

    # get account list
    account = get_account_id(service)

    # get profile information aobut the account being inquired
    profile = get_profile_id(service, account[0])

    # Send API request to Google Analytics and return the JSON element to the requesting entity
    return service.data().ga().get(
        ids = 'ga:' + profile[0][0],
        start_date = context.get("st_date"),
        end_date = context.get("end_date"),
        metrics = context.get("api_metric"),
        dimensions = context.get("api_dimension"),
        sort = context.get("sort_key"),
        filters = context.get("api_filter")
        ).execute()
