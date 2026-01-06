from main import scrape_web_impl

if __name__ == "__main__":
    content = scrape_web_impl(
        "https://github.com/alexeygrigorev/minsearch"
    )
    print(len(content))
