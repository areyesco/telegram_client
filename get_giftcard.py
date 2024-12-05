import re
from collections import Counter
import webbrowser
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import sys
import config
import utils

# Pre-compile the regex pattern for efficiency
LINK_PATTERN = re.compile(r'https://amzn\.to/\S+', re.IGNORECASE)


async def process_message(message):
    """
    Processes a message to identify if it contains specific keywords and links.
    For each unique link, fetches the page content asynchronously and checks for additional keywords.
    If conditions are met, opens the link in the default web browser.

    Parameters:
    message (str): The message text to be processed.
    """
    await utils.log_message("debug-> process_message: init")

    # List of initial keywords to identify in the message
    initial_keywords = config.INITIAL_KEYWORDS

    # Additional keywords to search for in the page content
    content_keywords = config.CONTENT_KEYWORDS

    # Convert message to lowercase for case-insensitive keyword search
    # Preprocess the message to replace escaped newline characters with actual newlines
    message = message.replace('\\n', '\n').replace('\\r', '\r').replace('\\"', '"').replace("\\'", "'")

    # Remove any leading/trailing quotes if present
    if message.startswith('"') and message.endswith('"'):
        message = message[1:-1]

    # Convert message to lowercase for case-insensitive keyword search
    message_lower = message.lower()

    # Check if any of the initial keywords are present in the message
    if any(keyword in message_lower for keyword in initial_keywords):
        # Find all links matching the specified format using regular expressions
        links = LINK_PATTERN.findall(message)
        await utils.log_message("debug-> links:", str(links))
        # Check if there are more than 5 links
        if len(links) > 5:
            await utils.log_message("more than 5 links")
            # Count the occurrences of each link
            link_counts = Counter(links)
            await utils.log_message("debug-> links_counts:", str(link_counts))
            
            # Sort the links from least to most frequent
            sorted_links = sorted(link_counts.items(), key=lambda x: x[1])
            await utils.log_message("debug-> sorted_links:", str(sorted_links))
            
            # Extract unique links, ordered by least frequent
            unique_links = [link for link, count in sorted_links]
            await utils.log_message(utils.Log_Level.INFO, "debug-> unique_links:", str(unique_links))

            # Process the links asynchronously
            await process_links_async(unique_links, content_keywords)
        else:
            await utils.log_message(utils.Log_Level.INFO, "\tThe message does not contain more than 5 links.")
    else:
        await utils.log_message(utils.Log_Level.INFO, "\tNo specified keywords found in the message.")
    await utils.log_message("debug-> end process_message")

async def process_links_async(links, content_keywords):
    # Limit the number of concurrent requests to avoid overwhelming the system
    await utils.log_message("debug-> process_links_async: init")
    semaphore = asyncio.Semaphore(10)  # Adjust the number as needed

    async with aiohttp.ClientSession() as session:
        tasks = []
        for link in links:
            await utils.log_message(utils.Log_Level.INFO, "\t\tLink:", str(link))
            await utils.log_message("debug-> process_links_async: link:", str(link))
            tasks.append(fetch_and_check_link(session, link, content_keywords, semaphore))
        await asyncio.gather(*tasks)
    print("debug-> process_links_async: end")

async def fetch_and_check_link(session, link, content_keywords, semaphore):
    await utils.log_message("debug-> fetch_and_check_link: init")
    async with semaphore:
        try:
            async with session.get(link, timeout=10) as response:
                await utils.log_message("debug-> fetch_and_check_link: response.status:", str(response.status))
                if response.status == 200:
                    content = await response.text()
                    
                    # Parse the HTML content using BeautifulSoup with lxml parser for speed
                    soup = BeautifulSoup(content, 'lxml')

                    # Extract the title and body text
                    title = soup.title.string if soup.title else ''
                    await utils.log_message("debug-> fetch_and_check_link: title:", str(title))
                    body_text = soup.get_text()

                    # Combine title and body for keyword search
                    page_content = f"{title} {body_text}"
                    
                    # Convert to lowercase once for efficiency
                    page_content_lower = page_content.lower()
                    #print("debug-> fetch_and_check_link: page_content_lower:", str(page_content_lower))

                    # Check if any of the content keywords are present
                    if any(keyword.lower() in page_content_lower for keyword in content_keywords):
                        # Open the link in the default web browser
                        await utils.log_message(utils.Log_Level.INFO, "\t\tOpen browser link:" + str(link) + " - Title:" + str(title) )
                        webbrowser.open(link)
                else:
                    await utils.log_message(utils.Log_Level.INFO, f"Error fetching {link}: HTTP status {response.status}")
        except Exception as e:
            await utils.log_message(f"Error fetching {link}: {e}")
    await utils.log_message("debug-> fetch_and_check_link: end")
