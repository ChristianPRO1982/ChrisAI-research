import scrapy


class MitSpider(scrapy.Spider):
    name = "mit"
    allowed_domains = ["dspace.mit.edu"]
    start_urls = ["https://dspace.mit.edu/discover?scope=%2F&query=artificial+intelligence&submit=Go&rpp=10&sort_by=dc.date.issued_dt&order=desc"]

    def parse(self, response):
        for item in response.css('.artifact-item'):
            yield item