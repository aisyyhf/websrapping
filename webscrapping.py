import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timedelta
import time

def scrape_articles_for_date(date):
    base_url = 'https://indeks.kompas.com'
    current_page = 1
    articles = []

    while True:
        website = f'{base_url}/?site=all&date={date}&page={current_page}'
        html = requests.get(website)
        text_html = html.text

        # Buat soup dari halaman utama
        soup = BeautifulSoup(text_html, 'lxml')

        # Temukan div dengan artikel
        box_div = soup.find('div', class_='articleList -list')

        # Jika box_div tidak ditemukan, hentikan proses
        if box_div is None:
            print(f"Tidak dapat menemukan div dengan kelas 'articleList -list' untuk tanggal {date}, halaman {current_page}")
            break

        # Temukan semua tag a dalam div
        tag_a = box_div.find_all('a')

        # Kumpulkan semua link artikel
        article_links = [item['href'] for item in tag_a]

        # Loop untuk setiap link artikel
        for idx, link in enumerate(article_links, start=1):
            # Permintaan HTTP ke link artikel
            article_html = requests.get(link)
            article_soup = BeautifulSoup(article_html.text, 'lxml')

            # Temukan judul artikel
            title_tag = article_soup.find('h1')
            title = title_tag.getText() if title_tag else "No Title Found"

            # Temukan tanggal rilis artikel
            timestamp_tag = article_soup.find('div', class_='read__time')
            timestamp = timestamp_tag.getText() if timestamp_tag else "No Timestamp Found"

            # Temukan isi artikel
            content_tag = article_soup.find('div', class_='read__content')
            if content_tag:
                clearfix_div = content_tag.find('div', class_='clearfix')
                if clearfix_div:
                    paragraphs = clearfix_div.find_all('p')
                    content = '\n'.join(p.getText().strip() for p in paragraphs if not p.find('strong'))
                else:
                    content = "No Content Found"
            else:
                content = "No Content Found"

            # Temukan tags artikel
            tags_tag = article_soup.find('div', class_='read__tagging mt1 clearfix')
            if tags_tag:
                tags = [tag.getText() for tag in tags_tag.find_all('a')]
            else:
                tags = []

            # Temukan penulis artikel
            author_tag = article_soup.find('div', class_='credit-title-name')
            if author_tag:
                authors = [author.getText() for author in author_tag.find_all('h6')]
            else:
                authors = []

            # Simpan data dalam dictionary
            article_data = {
                "Date": date,
                "ID": idx,
                "Title": title,
                "Timestamp": timestamp,
                "FullText": content,
                "Tags": ', '.join(tags),
                "Author": ', '.join(authors),
                "Url": link
            }

            # Tambahkan dictionary ke list articles
            articles.append(article_data)

        # Cek apakah ada halaman berikutnya
        next_page_link = soup.find('a', class_='paging__link', string=str(current_page + 1))
        if next_page_link:
            current_page += 1
            print(current_page)
        else:
            break

    return articles

def scrape_articles_for_year(year, output_filename):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 1, 31)
    delta = timedelta(days=1)

    current_date = start_date
    all_articles = []

    # Buat atau tambahkan ke file CSV
    with open(output_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Date", "ID", "Title", "Timestamp", "FullText", "Tags", "Author", "Url"])
        
        # Tulis header jika file baru
        if file.tell() == 0:
            writer.writeheader()
        
        while current_date <= end_date:
            print(f"Scraping articles for date: {current_date.strftime('%Y-%m-%d')}")
            try:
                articles = scrape_articles_for_date(current_date.strftime('%Y-%m-%d'))
                for article in articles:
                    writer.writerow(article)
            except Exception as e:
                print(f"Error occurred while scraping date {current_date.strftime('%Y-%m-%d')}: {e}")
            current_date += delta

if __name__ == "__main__":
    year = 2024
    output_filename = f'kompas_articles_{year}.csv'
    scrape_articles_for_year(year, output_filename)
