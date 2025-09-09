import requests
from bs4 import BeautifulSoup
import csv
import time
import re

def scrape_imdb_movies():
    """
    Scrape movie data from IMDb's Top Movies page
    """
    # IMDb URL for top movies (using their charts section)
    url = "https://www.imdb.com/chart/top/"
    
    # Headers to mimic a real browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Send GET request with headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all movie entries
        movie_elements = soup.find_all('li', class_='ipc-metadata-list-summary-item')
        
        movies_data = []
        
        for movie in movie_elements:
            try:
                # Extract movie title
                title_element = movie.find('h3', class_='ipc-title__text')
                title = title_element.get_text().split('. ')[1] if title_element else "N/A"
                
                # Extract year - look for year pattern in various elements
                year_text = ""
                year_elements = movie.find_all('span', class_='sc-b0691f29-8')
                for element in year_elements:
                    text = element.get_text()
                    if re.match(r'^\d{4}$', text):  # Match 4-digit years
                        year_text = text
                        break
                
                # If no year found, try alternative approach
                if not year_text:
                    year_span = movie.find('span', class_='cli-title-metadata-item')
                    if year_span:
                        year_text = year_span.get_text()
                
                # Extract rating (optional)
                rating_span = movie.find('span', class_='ipc-rating-star')
                rating = rating_span.get_text().split()[0] if rating_span else "N/A"
                
                # Extract categories/genres
                categories = []
                genre_elements = movie.find_all('span', class_='ipc-inline-list__item')
                for element in genre_elements:
                    genre_text = element.get_text().strip()
                    if genre_text and not genre_text.isdigit() and len(genre_text) > 2:
                        categories.append(genre_text)
                
                # Clean up categories list
                categories = [cat for cat in categories if not re.match(r'^\d', cat)]
                
                movies_data.append({
                    'title': title,
                    'year': year_text,
                    'rating': rating,
                    'categories': ', '.join(categories) if categories else "N/A"
                })
                
            except Exception as e:
                print(f"Error processing a movie: {e}")
                continue
        
        return movies_data
        
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def save_to_csv(movies_data, filename='movies_data.csv'):
    """
    Save movie data to a CSV file
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'year', 'rating', 'categories']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for movie in movies_data:
                writer.writerow(movie)
        
        print(f"Data successfully saved to {filename}")
        
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def display_movies(movies_data, limit=10):
    """
    Display movie data in a formatted way
    """
    print("\n" + "="*80)
    print(f"{'MOVIE DATABASE SCRAPER RESULTS':^80}")
    print("="*80)
    print(f"{'Title':<40} {'Year':<6} {'Rating':<6} {'Categories':<30}")
    print("-"*80)
    
    for i, movie in enumerate(movies_data[:limit]):
        title = movie['title'][:37] + '...' if len(movie['title']) > 40 else movie['title']
        categories = movie['categories'][:27] + '...' if len(movie['categories']) > 30 else movie['categories']
        
        print(f"{title:<40} {movie['year']:<6} {movie['rating']:<6} {categories:<30}")
        
        if i == limit - 1 and len(movies_data) > limit:
            print(f"\n... and {len(movies_data) - limit} more movies")
            break

def main():
    """
    Main function to run the web scraper
    """
    print("Starting IMDb movie scraper...")
    print("Please wait while we scrape movie data...")
    
    # Scrape the data
    movies_data = scrape_imdb_movies()
    
    if movies_data:
        print(f"Successfully scraped {len(movies_data)} movies!")
        
        # Display first 10 movies
        display_movies(movies_data)
        
        # Save to CSV file
        save_to_csv(movies_data)
        
        # Additional statistics
        years = [int(movie['year']) for movie in movies_data if movie['year'].isdigit()]
        if years:
            print(f"\nStatistics:")
            print(f"Earliest year: {min(years)}")
            print(f"Latest year: {max(years)}")
            print(f"Average year: {sum(years) // len(years)}")
        
    else:
        print("No movies were scraped. Please check your internet connection or try again later.")

if __name__ == "__main__":
    # Add a delay to be respectful to the server
    time.sleep(1)
    main()