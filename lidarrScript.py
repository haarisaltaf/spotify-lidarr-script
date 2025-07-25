"""
This script is to grab all of the albums listed in the exportify csv file then pass it through into lidarr to be downloaded.
"""
import csv
import requests

# Constants
# grab spotify data from exportify (output as csv)
CSVFILE = input("Enter the CSV File location: ").strip()
LIDARR_URI = "http://localhost:8686"
API_KEY = "your_api_key_here"
HEADERS = {"X-Api-Key": API_KEY}


def getAlbumsFromCSV(CSV_DICT):
    """
    Script to return a set of albums from the Exportify csv.
    """
    albums = []
    with open(CSVFILE, newline='') as file:
        CSV_DICT = csv.DictReader(file)
        for row in CSV_DICT:
            albums.append(row['Album Name'].strip())
    return set(albums)


def getArtistsFromCSV(CSV_DICT):
    """
    Script to return a set of albums from the Exportify csv.
    """
    artists = []
    for row in CSV_DICT:
        # adding both album and artist to list in format: [AlbumName, Artist1, artist2, etc.]
        albumWithArtist = [
            row['Album Name'].strip(), row['Artist Name(s)'].strip()]
        if albumWithArtist not in artists:
            artists.append(albumWithArtist)
    return artists


# ALBUMS = getAlbumsFromCSV(CSVFILE)
# print(ALBUMS)
# ARTIST = getArtistsFromCSV(CSVFILE)
# print(ARTIST)


def checkIfChange(LIST):
    """
    Remove the unwanted options from the passed through.
    """
    wantChanges = input("Would you like to change any of these: (Y/n)").lower()
    while (wantChanges != "y") and (wantChanges != "n"):
        wantChanges = input(
            "Y or N pls").lower()
    if wantChanges == "y":
        for i in range(len(LIST)-1):
            print(f"{i}: {LIST[i]},          {i+1}: {LIST[i+1]}")
        index = int(input(
            "Which number would you like to remove (input 1 number then click enter and will ask again, enter '-1' when finished): "))
        LIST.pop(index)
        while index != -1:
            index = int(
                input("Enter another to be removed (enter -1 to finish):  "))
            LIST.pop(index)
    return LIST


def requestLidarrAlbums(album):
    requestURL = f"{LIDARR_URI}/api/v1/album/lookup?term={album}"
    r = requests.get(requestURL, headers=HEADERS)
    if r.status_code == 200:
        results = r.json()[0]
        albumID = results['id']
        # Get full album details
        detailURL = f"{LIDARR_URI}/api/v1/album/{albumID}"
        detail = requests.get(detailURL, headers=HEADERS).json()
        detail['monitored'] = True

        # PUT update
        update = requests.put(detailURL, headers=HEADERS, json=detail)
        update.raise_for_status()

        print(f"✅ Album Monitored: {results['title']}, {
              results['artist']['artistName']}")
    else:
        print(f"Failed: {r.status_code}")


def main():
    # Grabs albums from csv file, creates counter filled with the albums failed and successful
    ALBUMS = checkIfChange(list(getAlbumsFromCSV(CSVFILE)))
    counter = []
    failedCounter = []
    for album in ALBUMS:
        # requests lidarr to monitor album and adds to counter, if fails then prints exceptions
        try:
            requestLidarrAlbums(album)
            counter.append(album)
        except Exception as e:
            failedCounter.append(album)
            print(f"Error finding album {album}: {e}")
    # Prints stats
    # print(f"Albums Added: {counter}\n\n")
    print(f"Total number of albums added: {len(counter)}")
    print(f"FAILED Albums: {failedCounter}\n\nTotal Failed Albums: {
          len(failedCounter)}")


if __name__ == "__main__":
    main()
