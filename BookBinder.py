import re
import requests

"""
This needs three components from the old one:

- ISBN Lookup
- UI
- Price lookuo
"""
def ValidateISBN(barcode):
    # This regex checks for ISBN-10 or ISBN-13
    regex = re.compile("^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:97[89])[- ]?\\d{10}$)[-0-9 ]{13}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?(?:[0-9]+[- ]?){2}[0-9X]$")

    if regex.search(barcode):
        # Remove non-ISBN digits and split into an array
        chars = list(re.sub("[^0-9X]", "", barcode))
        last = chars.pop()

        # ISBN-10 Check
        if len(chars) == 9:
            val = sum((x + 2) * int(y) for x, y, in enumerate(reversed(chars)))
            check = 11 - (val % 11)
            if check == 10:
                check = "X"
            else:
                check = "0"
        # ISBN-13 Check
        else:
            val = sum((x%2 * 2 + 1) * int(y) for x, y in enumerate(chars))
            check = 10 - (val % 10)
            if check == 10:
                check = "0"

        if str(check) == last:
            return True
        else:
            print("Invalid ISBN checkdigit")
            return False

    print("Invalid ISBN")
    return False

# WARN: 
def GetEbayPriceRanges(isbn):
    # NOTE: Searching by ISBN isn't always fully accurate
    # TODO: Set up rotating tokens
    oauthToken = ''

    # EBAY_GB is here used to change currency
    headers = {
        "Authorization" : f"Bearer {oauthToken}",
        "X-EBAY-C-MARKETPLACE-ID" : "EBAY_GB",
        "Content-Type" : "application/json"
    }
    
    url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={isbn}&limit=5"
    # Send request
    response = requests.get(url, headers = headers)

    if response.status_code == 200:
        # Collect data metrics
        prices = []
        items = response.json()['itemSummaries']
        for item in items:
            prices.append(item)

        priceInformation = {
            "Average" : sum(prices) / len(prices),
            "Low" : min(prices),
            "Max" : max(prices)
        }

        return priceInformation
    else:
        print(f"Error: {response.status_code}, {response.text}")


def GetISBNInfo(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if 'items' in data:
            bookInfo = data['items'][0]['volumeInfo']

            # Extract relevant information
            title = bookInfo.get('title', 'N/A')
            authors = ', '.join(bookInfo.get('authors', ['N/A']))
            publisher = bookInfo.get('publisher', 'N/A')
            publishedDate = bookInfo.get('publishedDate', 'N/A')
            description = bookInfo.get('description', 'No description available')
            pageCount = bookInfo.get('pageCount', 'N/A')
            categories = ', '.join(bookInfo.get('categories', ['N/A']))

            info = {
                "Title" : title,
                "Authors" : authors,
                "Publisher" : publisher,
                "Published Date" : publishedDate,
                "Description" : description,
                "Page Count" : pageCount,
                "Categories" : categories
            }

            return info

        else:
            print(f"No book found with ISBN: {isbn}")
    else:
        print(f"Error: Unable to retrieve data, failed with status code: {response.status_code})")
    # This guarantees an error 
    return False


def Main(barcode):
    # Error handling
    if ValidateISBN(barcode) == False:
        print("\n\nNot a valid ISBN code.")
        return
    else:
        print("Valid ISBN code provided.")

    bookInfo = GetISBNInfo(barcode)
    if not bookInfo:
        return
    
    # In theory a book should have been returned by this point
    for i in bookInfo:
        print(i, ":", bookInfo[i])

if __name__ == "__main__":
    while True:
        barcode = input("Scan ISBN code or enter it manually: ")
        if barcode == "quit" or barcode == "q" or barcode == "exit":
            exit(0)

        Main(barcode)
