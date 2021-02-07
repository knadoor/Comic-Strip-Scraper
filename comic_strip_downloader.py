# Dilbert comic strips downloader bot
# Date: 31st October, 2020.

from bs4 import BeautifulSoup
from requests.exceptions import Timeout
import datetime
import time
import requests


def main():
    # DEFINE VARIABLES
    # Original Publish Date: April 16, 1989
    total_comics = 0
    running_date = datetime.date(2021,1,25) # YYYY,MM,DD
    today = datetime.date.today()
    base_url = "https://dilbert.com/strip/"
    start_time = time.monotonic()

    print("Starting...\n")

    while(running_date <= today):
        t0_delay = time.time()
        parser(base_url, running_date)

        # Pause before scraping the next comic to prevent from getting disconnected by remote server
        response_delay = time.time() - t0_delay
        time.sleep(2*response_delay) # Wait 2x longer than it took the server to respond

        print(f"Next comic will be downloaded in {round(2*response_delay,2)} seconds.\n")
        running_date = running_date + datetime.timedelta(days=1)
        total_comics += 1
    
    end_time = time.monotonic()
    print(f"Completed operation! A total of {total_comics} comics was successfully downloaded in {round((end_time - start_time),2)} seconds.")
    

def parser(base_url, running_date):
    comic_link = base_url + str(running_date)
    exceptionComicDates = []

    # Spoof the User Agent so as to make the request come from a web browser and not a bot
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
    }

    # Handle network errors
    try:
        # If there's a timeout, wait 10 seconds
        page = requests.get(comic_link, headers=headers,timeout=10)
    
        # Create a bs4 object
        soup = BeautifulSoup(page.content, 'html.parser')

        # Find the Dilbert comic strip date
        comic_date = soup.find_all(class_='comic-title-date')
        for comic_date in comic_date:
            # Each comic_date is a new BeautifulSoup object.
            date = comic_date.find('span')
            year = comic_date.find('span',itemprop="copyrightYear")
            print(f"Date Published:\n{date.text} {year.text}\n")

        # Find the Dilbert comic strip title
        comic_title = soup.find_all(class_='comic-title-name')
        for comic_title in comic_title:
            if comic_title.text != "":
                print(f"Title: {comic_title.text}\n")

        # Find the Dilbert comic strip rating (out of 5)
        comic_ratings = soup.find_all(class_='comic-rating')[1]
        print("Rating:\n" + comic_ratings.get('data-total'))
        
        # Find the Dilbert comic strip transcript
        comic_transcript = soup.find_all(class_='comic-transcript')
        for comic_transcript in comic_transcript:
            print(comic_transcript.text)

        # Find the Dilbert comic strip link
        comic_img = soup.find_all(class_='img-responsive img-comic')
        for comic_img in comic_img:
            print(comic_img.get('src','n/a'))
        
        print("---------------")     

        comic_url = comic_img.get('src','n/a')
        downloadComic(comic_url, running_date)

    except requests.exceptions.RequestException:
        # If something unexpected occurs, wait 60 seconds before trying again
        exceptionComicDates.append(str(running_date))
        printExceptions(exceptionComicDates)
        print("Retrying in 60 seconds...\n")
        time.sleep(60)
        parser(base_url, running_date)


def printExceptions(exceptionComicDates):
    # Write contents of error to log file
    file = open("FailedComicsLog.txt", "a")
    print(f"Network connection issues has occurred.")
    file.write(f"Network connection issues has occurred.\n")

    print("The following comic (date shown) has failed to download, will retry the download:")
    file.write("The following comic (date shown) has failed to download, will retry the download:\n")
    for failed in exceptionComicDates:
        print(failed)
        file.write(failed + "\n")
    print("************************\n")
    file.write("************************\n\n")
    file.close()


# Download the comic strip
def downloadComic(comic_url, running_date):
    response = requests.get(comic_url)
    file = open(f"Dilbert Comic Strip - {running_date}.png", "wb")
    file.write(response.content)
    file.close()


if __name__ == "__main__":
    main()