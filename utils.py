from constants import MACYS_PRODUCT_URL_PREFIX

def verify_urls(urls):
    """Verify if URLs are valid Macy's product URLs"""
    valid_urls = []
    invalid_urls = []

    for url in urls:
        if url.startswith(MACYS_PRODUCT_URL_PREFIX):
            valid_urls.append(url)
        else:
            invalid_urls.append(url)

    return valid_urls, invalid_urls