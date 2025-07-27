"""
This script is to grab all of the albums listed in the exportify csv file then pass it through into lidarr to be downloaded.
"""
import csv
import requests
import os

# Constants
# grab spotify data from exportify (output as csv)
CSVFILE = input("Enter the CSV File location: ").strip()
LIDARR_URI = "http://localhost:8686"
API_KEY = os.getenv("LIDARR_API_KEY")
HEADERS = {"X-Api-Key": API_KEY}


def getAlbumsFromCSV():
    """
    Script to return a set of albums from the Exportify csv.
    """
    albums = []
    with open(CSVFILE, newline='') as file:
        CSV_DICT = csv.DictReader(file)
        for row in CSV_DICT:
            albums.append(row['Album Name'].strip())
    return set(albums)


def getArtistsFromCSV():
    """
    Script to return a set of albums from the Exportify csv.
    """
    artists = []
    with open(CSVFILE) as file:
        CSV_DICT = csv.DictReader(file)
        for row in CSV_DICT:
            albumRow = row['Artist Name(s)'].strip()
            # now only grabbing the first (main) artist from the row
            if albumRow not in artists:
                artists.append("Tyler, the Creator")
                if "," in albumRow:
                    artists.append(albumRow[:albumRow.index(",")])
                else:
                    artists.append(albumRow)
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

        print(f"Album Monitored: {results['title']}, {
              results['artist']['artistName']}")
    else:
        print(f"Failed: {r.status_code}")


def main():
    ARTIST = set(getArtistsFromCSV())
    print(f"{ARTIST}\n{len(ARTIST)}")
    # Grabs albums from csv file, creates counter filled with the albums failed and successful
    counter = []
    failedCounter = []
    for artist in ARTIST:
        # requests lidarr to monitor album and adds to counter, if fails then prints exceptions
        try:
            requestLidarrAlbums(artist)
            counter.append(artist)
        except Exception as e:
            failedCounter.append(artist)
            print(f"Error finding artist {artist}: {e}")
    # Prints stats
    # print(f"Albums Added: {counter}\n\n")
    print(f"Total number of artists added: {len(counter)}")
    print(f"FAILED aritsts: {failedCounter}\n\nTotal Failed artists: {
          len(failedCounter)}")


if __name__ == "__main__":
    main()
