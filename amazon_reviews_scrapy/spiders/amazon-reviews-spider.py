import scrapy
import urllib.parse


class AmazonReviewsSpider(scrapy.Spider):
    name = 'amazon-reviews-spider'

    def __init__(self, product_id=None, *args, **kwargs):
        super(AmazonReviewsSpider, self).__init__(*args, **kwargs)

        if not product_id:
            raise Exception("product_id is required")

        self.start_urls = ['https://www.amazon.com/product-reviews/' +
                           product_id +
                           '/ref=cm_cr_arp_d_viewopt_rvwer?ie=UTF8&showViewpoints=1&pageNumber=1&reviewerType=all_reviews']

    def parse(self, response):
        yield from self.extract_pages(response)
        yield from self.extract_reviews(response)

    def parse_reviews(self, response):
        yield from self.extract_reviews(response)

    def extract_reviews(self, response):
        for review in response.css('div[data-hook=review]'):
            yield {
                'id': review.xpath('@id').extract_first(),
                'stars': self.extract_stars(review),
                'title': review.css('a.review-title::text').extract_first(),
                'author_profile_url': review.css('a[data-hook="review-author"]::attr(href)').extract_first(),
                'author_name': review.css('a[data-hook="review-author"]::text').extract_first(),
                'badges': review.css('span.c7y-badge-text::text').extract(),
                'review_date': review.css('span.review-date::text').extract_first(),
                'review_text': '\n'.join(review.css('span.review-text::text').extract()),
                'comments_count': review.css('span.review-comment-total::text').extract_first(),
                'review_helpful_votes': self.extract_review_votes(review)
            }

    def extract_review_votes(self, review):
        votes = review.css('span.review-votes::text').extract_first()
        if not votes:
            return 0
        votes = votes.strip().split(' ')
        if not votes:
            return 0
        return votes[0].replace(',', '')

    def extract_stars(self, review):
        stars = None
        star_classes = review.css('i.a-icon-star::attr(class)').extract_first().split(' ')
        for i in star_classes:
            if i.startswith('a-star-'):
                stars = int(i[7:])
                break
        return stars

    def extract_pages(self, response):
        page_links = response.css('span[data-action="reviews:page-action"] li')
        base_parts = urllib.parse.urlsplit(self.start_urls[0])
        
        if len(page_links) > 2:
            last_page_url = page_links[-2].css('a::attr(href)').extract_first()
            url_parts = urllib.parse.urlsplit(last_page_url)
            qs = urllib.parse.parse_qs(url_parts.query)
            last_page_number = int(qs.get('pageNumber', [1])[0])
            self.logger.info('last page number ' + repr(last_page_number))
            if last_page_number > 1:
                url_parts = list(url_parts)
                url_parts[0] = base_parts.scheme
                url_parts[1] = base_parts.netloc
                url_parts[3] = qs

                for i in range(2, last_page_number + 1):
                    qs["pageNumber"] = i
                    url_parts[3] = urllib.parse.urlencode(qs, doseq=True)
                    self.logger.info('url ' + repr(url_parts))
                    yield scrapy.Request(urllib.parse.urlunsplit(url_parts), self.parse_reviews)



